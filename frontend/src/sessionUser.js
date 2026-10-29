export function sessionUserName() {
  const info = window.user_info
  const name = info?.full_name || info?.email || window.session_user
  if (!name || name === 'Guest') return 'Signed in'
  return name
}
