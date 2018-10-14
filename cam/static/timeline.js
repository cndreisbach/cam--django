/* globals superagent, Stimulus */

const request = superagent

class TimelineController extends Stimulus.Controller {
  connect () {}

  loadMore (event) {
    event.preventDefault()

    if (this.offset < this.total) {
      this.setLoading(true)
      let timelineReq = request
        .get('/')
        .query({ offset: this.offset, limit: this.limit })

      if (this.startDate) {
        timelineReq.query({ start: this.startDate })
      }

      timelineReq
        .set('X-Requested-With', 'XMLHttpRequest')
        .then(response => response.text)
        .then(html => {
          this.element
            .querySelector('#posts')
            .insertAdjacentHTML('beforeend', html)
          this.offset += this.limit
          this.setLoading(false)
        })
    }
  }

  setLoading (status) {
    if (status) {
      this.element.querySelector('#load-more').classList.add('is-loading')
    } else {
      this.element.querySelector('#load-more').classList.remove('is-loading')
    }
  }

  showImage (event) {
    const imageUrl = event.target.dataset.imageUrl
    const modal = document.getElementById('photo-modal')
    modal.querySelector('img').src = imageUrl
    modal.classList.add('is-active')
  }

  hideImage (event) {
    const modal = document.getElementById('photo-modal')
    modal.classList.remove('is-active')
  }

  get offset () {
    return parseInt(this.data.get('offset'))
  }

  set offset (value) {
    this.data.set('offset', value)
  }

  get limit () {
    return parseInt(this.data.get('limit'))
  }

  get total () {
    return parseInt(this.data.get('total'))
  }

  get startDate () {
    return this.data.get('startDate')
  }
}

(() => {
  const application = Stimulus.Application.start()

  application.register('timeline', TimelineController)
})()
