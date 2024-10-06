#!/bin/bash

# Verifica se il file install_and_run.command esiste
if [[ ! -f "ConvertFolderToWept.command" ]]; then
    echo "Errore: il file ConvertFolderToWept.command non esiste nella directory."
    exit 1
fi

# Rendi il file install_and_run.command eseguibile
chmod +x ConvertFolderToWept.command

# Esegui il file install_and_run.command
./install_and_run.command

# Opzionale: Elimina questo script di avvio automatico
rm -- "$0"
