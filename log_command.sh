# >> activity-tracker shell hook
function _at_log_command() {
  local EXIT=$?
  local CMD=$(history 1 | sed 's/^ *[0-9]* *//')
  # escreve localmente (evita dependências)
  echo "$(date +%s) | terminal | ${CMD}" >> ~/.activity_tracker/term_history.log
  # opcional: enviar para API (uncomment se quer)
  # curl -s -X POST http://localhost:5001/api/events -H "Content-Type: application/json" -d "{\"ts\":$(date +%s),\"type\":\"terminal\",\"title\":\"cmd\",\"detail\":\"${CMD}\"}" >/dev/null 2>&1
  return $EXIT
}
export PROMPT_COMMAND=_at_log_command
# << activity-tracker shell hook
