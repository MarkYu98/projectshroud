from threading import Thread

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import Http404, HttpResponse, FileResponse
from urllib.parse import quote

from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.serializers import ValidationError

from backend.serializers import *
from backend.permissions import *
from backend.utils.qrcode import text_to_qr
from backend.utils.email import send_activation_email, send_registered_email
from backend.utils.excel import *


def check_is_admin(user, event):
    if not isinstance(user, get_user_model()):
        return False
    if user.is_site_admin:
        return True
    return UserManageEvent.objects.filter(user=user, event=event).exists()


def check_is_admin_not_site_admin(user, event):
    return UserManageEvent.objects.filter(user=user, event=event).exists()


def check_event_registered(user, event):
    return UserRegisterEvent.objects.filter(user=user, event=event).exists()


def check_event_register_approved(user, event):
    return UserRegisterEvent.objects.filter(user=user, event=event, approved=True).exists()


@api_view(['GET', 'POST'])
def activate_user(request):
    if 'token' not in request.data:
        raise ValidationError('No token provided.')

    try:
        user = get_user_model().objects.get(activate_token=request.data.get('token'))
    except get_user_model().DoesNotExist:
        raise ValidationError('Invalid token.')

    if user.is_activated:
        raise ValidationError('Already activated.')

    if user.activate_token is not None:
        user.activate()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsSiteAdminOrSelf))
def send_activation(request):
    user = request.user
    data = request.GET
    if 'user_id' in data:
        try:
            user = get_user_model().objects.get(id=data.get('user_id'))
        except get_user_model().DoesNotExist:
            raise ValidationError('User Not Found.')

    if user is None or isinstance(user, AnonymousUser):
        raise ValidationError('No User Specified.')
    if user.is_activated:
        raise ValidationError('Already activated.')

    user.generate_activate_token()
    send_activation_email(user)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def gen_qrcode(request):
    if 'text' not in request.data:
        raise ValidationError('No text provided.')

    text = request.data.get('text')
    qr_img = text_to_qr(text)

    return HttpResponse(qr_img, content_type='image/png')


class DummyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'status': 'request was permitted',
            'is_activated': request.user.is_activated
        }
        return Response(content)


class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        serializer = UserProfileSerializer(instance=request.user)
        return Response(serializer.data)


class UserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated, IsSiteAdminOrSelf)


class EventList(generics.ListCreateAPIView):
    queryset = Event.objects.filter(public=True)
    serializer_class = EventListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsActivatedOrReadOnly)

    def perform_create(self, serializer):
        # user = get_user_model().objects.get(id=self.request.data.get('host_id', ''))
        user = self.request.user
        desc = ''

        if 'description' in self.request.data:
            desc = self.request.data.get('description')

        event_obj = serializer.save(host=user, description=desc)

        ume_obj = UserManageEvent(user=user, event=event_obj)
        ume_obj.save()


class PastEventList(generics.ListAPIView):
    queryset = Event.objects.filter(public=True, end_time__lte=timezone.now())
    serializer_class = EventListSerializer


class FutureEventList(generics.ListAPIView):
    queryset = Event.objects.filter(public=True, start_time__gt=timezone.now())
    serializer_class = EventListSerializer


class OngoingEventList(generics.ListAPIView):
    queryset = Event.objects.filter(public=True, start_time__lte=timezone.now(), end_time__gt=timezone.now())
    serializer_class = EventListSerializer


class UserRegisterEventList(generics.ListAPIView):
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf)

    def get_queryset(self):
        # user = get_user_model().objects.get(id=self.kwargs.get('pk'))
        user = self.request.user
        return UserRegisterEvent.objects.filter(user=user)


class UserManageEventList(generics.ListAPIView):
    serializer_class = UserManageEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf)

    def get_queryset(self):
        # user = get_user_model().objects.get(id=self.kwargs.get('pk'))
        user = self.request.user
        return UserManageEvent.objects.filter(user=user)


class UserRegisterFutureEventList(generics.ListAPIView):
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf)

    def get_queryset(self):
        # user = get_user_model().objects.get(id=self.kwargs.get('pk'))
        user = self.request.user
        return UserRegisterEvent.objects.filter(user=user, event__start_time__gt=timezone.now())


class UserRegisterPastEventList(generics.ListAPIView):
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf)

    def get_queryset(self):
        # user = get_user_model().objects.get(id=self.kwargs.get('pk'))
        user = self.request.user
        return UserRegisterEvent.objects.filter(user=user, event__end_time__lte=timezone.now())


class UserRegisterOngoingEventList(generics.ListAPIView):
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf)

    def get_queryset(self):
        # user = get_user_model().objects.get(id=self.kwargs.get('pk'))
        user = self.request.user
        return UserRegisterEvent.objects.filter(user=user, event__start_time__lte=timezone.now(),
                                                event__end_time__gt=timezone.now())


class UserEventRegister(generics.CreateAPIView):
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated)

    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data
        if 'user_id' in data:
            try:
                user = get_user_model().objects.get(id=data.get('user_id'))
            except Event.DoesNotExist:
                raise ValidationError('User Not Found.')

        if 'event_id' not in data:
            raise ValidationError('No event_id specified.')

        try:
            event = Event.objects.get(id=data.get('event_id'))
        except Event.DoesNotExist:
            raise ValidationError('Event Not found.')

        if check_event_registered(user, event):
            if check_event_register_approved(user, event):
                raise ValidationError('Already Registered.')
            else:
                raise ValidationError('Already applied, waiting for approval.')

        if event.require_approve:
            if event.require_application:
                if 'application_text' not in data or data.get('application_text') == '':
                    raise ValidationError('Need to provide application info.')
            serializer.save(user=user, event=event, transport=None, approved=False)
            event.newregistration()
            send_registered_email(user, event, approved=False)

        else:
            transport = None
            if 'transport_id' in data:
                try:
                    transport = Transport.objects.get(id=data.get('transport_id'))
                except Event.DoesNotExist:
                    raise ValidationError('Transport Not found.')
            serializer.save(user=user, event=event, transport=transport, approved=True)
            event.newregistration()
            send_registered_email(user, event, approved=True)


class UserEventConflict(APIView):
    queryset = UserRegisterEvent.objects.all()
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf|IsSiteAdminOrEventManager)

    def post(self, request, format=None):
        data = request.data

        user = request.user
        if 'user_id' in data:
            try:
                user = get_user_model().objects.get(id=data.get('user_id'))
            except get_user_model().DoesNotExist:
                raise ValidationError('User Not Found.')

        event = Event.objects.get(id=data.get('event_id'))

        if check_event_registered(user, event):
            if check_event_register_approved(user, event):
                raise ValidationError('Already Registered this event.')
            else:
                raise ValidationError('Already applied this event, waiting for approval.')

        ret_data = {}
        lst = UserRegisterEvent.objects.filter(user=user,
                                            event__start_time__lte=event.end_time,
                                            event__end_time__gte=event.start_time)
        if lst.exists():
            ret_data['conflict'] = True
            if 'user_id' not in data:
                ret_data['user_register_event'] = UserRegisterEventSerializer(lst[0]).data
            return Response(ret_data)

        ret_data['conflict'] = False

        return Response(ret_data)


class ApproveEventRegister(APIView):
    queryset = UserRegisterEvent.objects.all()
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)

    def post(self, request, format=None):
        data = request.data
        if 'approve' not in data:
            raise ValidationError('Need to provide "approve" (Boolean) field.')

        approve = data['approve']
        if 'user_id' not in data:
            raise ValidationError('No user specified.')
        try:
            user = get_user_model().objects.get(id=data.get('user_id'))
        except get_user_model().DoesNotExist:
            raise ValidationError('User Not Found.')

        event = Event.objects.get(id=data.get('event_id'))

        try:
            ure_obj = UserRegisterEvent.objects.get(user=user, event=event)
        except UserRegisterEvent.DoesNotExist:
            raise ValidationError('Not registered/applied.')

        if approve:
            if ure_obj.approved:
                raise ValidationError('Already Approved.')
            ure_obj.approve()
            event.newapproved()

        if not approve:
            event.newunregistration(approve)
            ure_obj.reject()
            ure_obj.delete()

        return Response(status=status.HTTP_200_OK)


class UserEventUnregister(APIView):
    queryset = UserRegisterEvent.objects.all()
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf|IsSiteAdminOrEventManager)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        if 'user_id' in data:
            user = get_user_model().objects.get(id=data.get('user_id'))

        event = Event.objects.get(id=data.get('event_id'))
        if not check_event_registered(user, event):
            raise ValidationError('Not registered.')

        ure_obj = UserRegisterEvent.objects.get(user=user, event=event)
        if ure_obj.checked_in:
            raise ValidationError('Already checked in.')
        if ure_obj.transport is not None:
            ure_obj.transport.delete()

        event.newunregistration(ure_obj.approved)

        ure_obj.delete()
        return Response(status=status.HTTP_200_OK)


class AssignEventAdmin(generics.CreateAPIView):
    # Not Tested

    serializer_class = UserManageEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)

    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data
        if 'user_id' in data:
            try:
                user = get_user_model().objects.get(id=data.get('user_id'))
            except Event.DoesNotExist:
                raise ValidationError('User Not Found.')

        event = Event.objects.get(id=data.get('event_id'))
        if check_is_admin_not_site_admin(user, event):
            raise ValidationError('Is admin already.')

        serializer.save(user=user, event=event)


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    permission_classes = (IsEventHostAdminOrReadOnly|IsAdminUser,)
    pk_type = 'event'

    def get(self, request, *args, **kwargs):
        try:
            obj = Event.objects.get(pk=kwargs.get('pk'))
        except Event.DoesNotExist:
            raise Http404
        data = self.retrieve(request, *args, **kwargs).data

        data['event_admin'] = check_is_admin(request.user, obj)
        try:
            ure_obj = UserRegisterEvent.objects.get(user=request.user, event=obj)
            data['event_registered'] = True
            data['user_register_event'] = UserRegisterEventSerializer(ure_obj).data
        except UserRegisterEvent.DoesNotExist:
            data['event_registered'] = False

        return Response(data)


class EventAttendeeList(generics.ListAPIView):
    serializer_class = UserRegisterEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated)
    pk_type = 'event'

    def get_queryset(self):
        try:
            event = Event.objects.get(pk=self.kwargs.get('pk'))
        except Event.DoesNotExist:
            return None
        if not check_is_admin(self.request.user, event):
            raise ValidationError('Not Authorized.')
        return UserRegisterEvent.objects.filter(event=event)


class EventAdminList(generics.ListAPIView):
    serializer_class = UserManageEventSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated)
    pk_type = 'event'

    def get_queryset(self):
        try:
            event = Event.objects.get(pk=self.kwargs.get('pk'))
        except Event.DoesNotExist:
            return None
        if not check_is_admin(self.request.user, event):
            raise ValidationError('Not Authorized.')
        return UserManageEvent.objects.filter(event=event)


class TransportCreateView(generics.CreateAPIView):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer
    permission_classes = (permissions.IsAuthenticated, IsSiteAdminOrSelf|IsSiteAdminOrEventManager)

    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data
        if 'user_id' in data:
            user = get_user_model().objects.get(id=data['user_id'])

        event = Event.objects.get(id=data.get('event_id'))
        try:
            tp_obj = Transport.objects.get(user=user, event=event)
            tp_obj.delete()
        except Transport.DoesNotExist:
            pass
        finally:
            tp_obj = serializer.save(user=user, event=event)

        try:
            ure_obj = UserRegisterEvent.objects.get(user=user, event=event)
            ure_obj.transport = tp_obj
            ure_obj.save()
        except UserRegisterEvent.DoesNotExist:
            pass


class TransportView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner|IsEventHostAdmin|IsAdminUser)
    pk_type = 'transport'


class EventCheckInList(generics.ListCreateAPIView):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)
    pk_type = 'event'

    def get_queryset(self):
        queryset = super(EventCheckInList, self).get_queryset()
        return queryset.filter(event__pk=self.kwargs.get('pk'))

    def perform_create(self, serializer):
        serializer.save(event_id=self.kwargs.get('pk'))


class UserCheckInEvent(APIView):
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrSelf|IsSiteAdminOrEventManager)
    pk_type = 'checkin'

    def post(self, request, pk, format=None):
        try:
            checkinobj = CheckIn.objects.get(pk=pk)
        except CheckIn.DoesNotExist:
            raise Http404

        if not checkinobj.started:
            raise ValidationError('Check-in not enabled.')
        user = request.user
        if 'user_id' in request.data:
            try:
                user = get_user_model().objects.get(id=request.data.get('user_id'))
            except get_user_model().DoesNotExist:
                raise ValidationError('User not found.')

        try:
            ure_obj = UserRegisterEvent.objects.get(user=user, event=checkinobj.event)
        except UserRegisterEvent.DoesNotExist:
            raise ValidationError('Not registered.')

        if not ure_obj.approved:
            raise ValidationError('Registration not approved.')

        self.check_object_permissions(request, ure_obj)
        if ure_obj.checked_in and UserCheckIn.objects.filter(ure=ure_obj, checkin=checkinobj).exists():
            raise ValidationError('Already checked in.')

        uc_obj = UserCheckIn(ure=ure_obj, checkin=checkinobj)
        uc_obj.save()

        checkinobj.newcheckin()

        if not ure_obj.checked_in:
            ure_obj.checkin()
            ure_obj.save()

        return Response(status=status.HTTP_202_ACCEPTED)


class ToggleCheckIn(APIView):
    serializer_class = CheckInSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)
    pk_type = 'checkin'

    def post(self, request, pk, format=None):
        try:
            obj = CheckIn.objects.get(pk=pk)
        except CheckIn.DoesNotExist:
            raise Http404
        obj.toggle()
        obj.save()

        return Response(CheckInSerializer(obj).data, status=status.HTTP_202_ACCEPTED)


class DeleteCheckIn(generics.DestroyAPIView):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)
    pk_type = 'checkin'


class ExportExcel(APIView):
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)
    pk_type = 'event'

    def get(self, request, pk, format=None):
        try:
            event = Event.objects.get(pk=pk)
            file_path, file_name = export_excel(event)
            response = FileResponse(open(file_path, 'rb'))
            response['content_type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename=' + quote(file_name)
            return response
        except Exception:
            raise


class ImportExcel(APIView):
    permission_classes = (permissions.IsAuthenticated, IsActivated, IsSiteAdminOrEventManager)
    pk_type = 'event'

    def post(self, request, pk, format=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404
        try:
            file = request.FILES['file']
        except Exception:
            raise ValidationError('No file uploaded.')
        if file.name.split('.')[-1] != 'xlsx':
            raise ValidationError('Not a .xlsx file.')

        channel_layer = get_channel_layer()
        send = async_to_sync(channel_layer.group_send)
        group_name = 'event_%s_import' % event.id

        def callback(data):
            send(group_name, {
                'type': 'import_message',
                'message': data
            })

        t = Thread(target=import_excel, args=(event, file, callback))
        t.start()

        return Response(status=status.HTTP_202_ACCEPTED)


class DownloadExcelTemplate(APIView):
    permission_classes = (permissions.IsAuthenticated, IsActivated)
    pk_type = 'event'

    def get(self, request, format=None):
        file_path = get_import_template()
        response = FileResponse(open(file_path, 'rb'))
        response['content_type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=' + quote(os.path.basename(IMPORT_TEMPLATE_FILE_PATH))
        return response

