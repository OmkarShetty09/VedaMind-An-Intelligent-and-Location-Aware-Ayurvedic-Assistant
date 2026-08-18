export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isValidPassword(password) {
  return password.length >= 8;
}

export function isValidDisplayName(name) {
  return name.trim().length >= 2 && name.trim().length <= 60;
}
