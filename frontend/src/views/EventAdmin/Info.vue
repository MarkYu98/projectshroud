<template>
  <b-row>
    <b-col md="8">
      <b-form-group
        id="titleInputGroup"
        label-cols-sm="4"
        label-cols-lg="3"
        :label="$t('Title')"
        label-for="titleInput"
      >
        <b-form-input
          id="titleInput"
          v-model="event.title"
          required
        />
      </b-form-group>
      <b-form-group
        id="startTimeInputGroup"
        label-cols-sm="4"
        label-cols-lg="3"
        :label="$t('Start time')"
        label-for="startTimeInput"
      >
        <time-picker
          id="startTimeInput"
          v-model="event.startTime"
        />
      </b-form-group>
      <b-form-group
        id="endTimeInputGroup"
        label-cols-sm="4"
        label-cols-lg="3"
        :label="$t('End time')"
        label-for="endTimeInput"
      >
        <time-picker
          id="endTimeInput"
          v-model="event.endTime"
        />
      </b-form-group>
      <b-form-group
        id="locationInputGroup"
        label-cols-sm="4"
        label-cols-lg="3"
        :label="$t('Location')"
        label-for="locationInput"
      >
        <location-input
          id="locationInput"
          v-model="event.location"
        />
      </b-form-group>

      <b-form-group
        id="publicInputGroup"
        label-cols-sm="4"
        label-cols-lg="3"
        :label="$t('Is public?')"
        label-for="publicInput"
      >
        <div style="text-align: left;">
          <b-form-checkbox
            v-model="event.public"
            size="lg"
            switch
          />
        </div>
      </b-form-group>

      <b-form-group
        id="publicInputGroup"
        label-cols-sm="4"
        label-cols-lg="3"
        :label="$t('Require approve?')"
        label-for="publicInput"
      >
        <div style="text-align: left;">
          <b-form-checkbox
            v-model="event.requireApprove"
            size="lg"
            switch
          />
        </div>
      </b-form-group>

      <b-button
        variant="primary"
        :disabled="isLoading"
        @click="onSubmit"
      >
        {{ newEvent ? $t('Create') : $t('Save') }}
      </b-button>

      <b-button
        v-if="!newEvent"
        class="ml-5"
        variant="danger"
        :disabled="isLoading"
        @click="$refs['modal-delete'].show()"
      >
        {{ $t('Delete') }}
      </b-button>

      <b-modal
        ref="modal-delete"
        :title="$t('Confirm Deletion')"
        :ok-title="$t('OK')"
        :cancel-title="$t('Cancel')"
        lazy
        @show="deleteInput = ''"
        @shown="$refs.deleteConfirmInput.focus()"
        @ok.prevent="deleteEvent"
      >
        <b-form @submit.prevent="deleteEvent">
          <b-form-input
            ref="deleteConfirmInput"
            v-model="deleteInput"
            :state="deleteInputState"
            :placeholder="$t('Enter message \'\'', [confirmMessage])"
          />
          <b-form-text v-if="isLoading">
            {{ $t('Deleting... Hold on a minute please...') }}
          </b-form-text>
        </b-form>
      </b-modal>
    </b-col>
  </b-row>
</template>

<script>
import { BForm, BFormGroup, BFormInput, BFormCheckbox, BButton } from 'bootstrap-vue'
import TimePicker from '@/components/TimePicker.vue'
import LocationInput from '@/components/LocationInput.vue'

export default {
  name: 'EventAdminInfo',
  components: {
    TimePicker,
    LocationInput,
    BForm,
    BFormGroup,
    BFormInput,
    BFormCheckbox,
    BButton
  },
  props: {
    newEvent: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      event: {
        title: '',
        startTime: null,
        endTime: null,
        location: '',
        public: true,
        requireApprove: false
      },
      deleteInput: ''
    }
  },
  computed: {
    deleteInputState () {
      return this.deleteInput === this.confirmMessage
    },
    confirmMessage () {
      return this.$t('I am sure')
    }
  },
  watch: {
    '$route': 'refresh'
  },
  created () {
    if (!this.newEvent) {
      this.refresh()
    }
  },
  methods: {
    async refresh () {
      const res = await this.axios.get(`/api/event/${this.$route.params.id}/`)
      this.event = res.data
    },
    async onSubmit () {
      if (this.newEvent) {
        const res = await this.axios.post('/api/event/', this.event)
        this.$router.push('/event/' + res.data.id)
      } else {
        const res = await this.axios.patch(`/api/event/${this.$route.params.id}/`, this.event)
        this.event = res.data
        this.toastSuccess(this.$t('Event "" saved successfully', [res.data.title]))
      }
    },
    async deleteEvent () {
      if (!this.deleteInputState) {
        return
      }
      await this.axios.delete(`/api/event/${this.$route.params.id}/`)
      this.toastSuccess(this.$t('Successfully delete event ', [this.event.title]))
      this.$router.push('/admin-event')
    }
  }
}
</script>
