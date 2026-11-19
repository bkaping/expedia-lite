if (location.pathname.startsWith('/stillpoint')) {
  document.title = 'Stillpoint · Assignment 3 archive'
  import('./stillpoint.js')
} else {
  import('./market.js')
}
