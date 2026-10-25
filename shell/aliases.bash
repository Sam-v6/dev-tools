# Source this file after any existing ls aliases in ~/.bashrc.
_dev_tools_shell_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

_dev_tools_ls() {
    python3 "$_dev_tools_shell_dir/repo-ls.py" "$@"
}

alias ls='_dev_tools_ls'
alias ll='_dev_tools_ls -lh'
alias la='_dev_tools_ls -lah'
alias lt='_dev_tools_ls --tree'
