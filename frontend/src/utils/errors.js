export function messageForError(err) {
  return err?.data?.error?.message || err?.data?.message || err?.message || "Something went wrong";
}
