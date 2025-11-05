#!/bin/bash
# >> activity-tracker shell hook
# Adicione ao final do ~/.bashrc ou ~/.zshrc:
# source /caminho/para/log_command.sh

function _at_log_command() {
  local EXIT=$?
  local CMD=$(history 1 | sed 's/^ *[0-9]* *//')
  
  # Ignora comandos vazios ou muito pequenos
  if [ -z "$CMD" ] || [ ${#CMD} -lt 2 ]; then
    return $EXIT
  fi
  
  # Cria diretório se não existir
  mkdir -p ~/.activity_tracker
  
  # Escreve no arquivo local
  echo "$(date +%s)|terminal|${CMD}" >> ~/.activity_tracker/term_history.log
  
  # Envia para API (em background, sem bloquear o terminal)
  (
    curl -s -X POST http://localhost:5001/api/log_event \
      -H "Content-Type: application/json" \
      -d "{\"ts\":$(date +%s),\"type\":\"terminal\",\"title\":\"$(hostname)\",\"detail\":\"${CMD//\"/\\\"}\"}" \
      >/dev/null 2>&1 &
  )
  
  return $EXIT
}

# Para bash
if [ -n "$BASH_VERSION" ]; then
  export PROMPT_COMMAND="_at_log_command; $PROMPT_COMMAND"
fi

# Para zsh
if [ -n "$ZSH_VERSION" ]; then
  precmd_functions+=(_at_log_command)
fi

echo "ActivityTracker shell hook loaded"
# << activity-tracker shell hook
