#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    if [ "$EUID" = 0 ]; then
      echo "this script cannot be run with root";
    else
      # Mac OS X
      brew tap homebrew/cask-versions
      brew install openscad-snapshot --appdir .

      # rename so a stable openscad isn't overwritten
      mv ./OpenSCAD.app /Applications/OpenSCAD-nightly.app

      # Makes a sym link because the cli is just inside openscad
      echo "Please enter your password to create a symbolic link"
      sudo ln -sf /Applications/OpenSCAD-nightly.app/Contents/MacOS/OpenSCAD /usr/local/bin/openscad-nightly
    fi
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    if [ "$EUID" -ne 0 ]; then
      echo "Please run with root";
    else
      # GNU/Linux
      if which snap &>/dev/null; then
        echo "Installing snap..."
        sudo snap install openscad-nightly
      else
        echo "Installing AppImage..."

        # getting the AppImage and dependencies install script
        wget "https://files.openscad.org/snapshots/OpenSCAD-2023.02.15.ai13654-x86_64.AppImage"
        wget https://raw.githubusercontent.com/openscad/openscad/master/scripts/uni-get-dependencies.sh

        # rename
        mv OpenSCAD-2023.02.15.ai13654-x86_64.AppImage openscad-nightly

        # execute permissions
        chmod +x openscad-nightly uni-get-dependencies.sh

        # run and remove dependencies script
        ./uni-get-dependencies.sh
        rm uni-get-dependencies.sh

        # Move to bin
        mv openscad-nightly /usr/local/bin
        fi
    fi
fi

