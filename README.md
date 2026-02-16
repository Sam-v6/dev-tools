# 🖥️ Modern Ubuntu 24.04 Terminal Setup

A clean, fast, fully open-source terminal environment optimized for development, productivity, and aesthetics — without Snap, closed-source tools, or heavy desktop dependencies.

This setup uses modern Rust-based CLI tools and a GPU-accelerated terminal for a polished “senior-engineer workstation” experience.

---

## 📦 Components

### 🧪 Terminal Emulator — Ghostty

Modern GPU-accelerated terminal with excellent font rendering, themes, and performance.

* Open source
* Native performance (no Electron)
* Tabs, splits, transparency
* Clean GTK integration

**Install (native .deb build)**

```bash
# Example using downloaded .deb
sudo apt install ./ghostty_*_amd64_24.04.deb
```

**Config file**

```
~/.config/ghostty/config
```

**Recommended settings**

```ini
font-family = "JetBrainsMono Nerd Font"
font-size = 13

theme = "Catppuccin Mocha"

gtk-titlebar = false
window-decoration = none

background-opacity = 0.96

window-padding-x = 12
window-padding-y = 12

cursor-style = block
cursor-blink = true
```

---

### 🔤 Font — Nerd Font (JetBrains Mono)

Required for icons, powerline glyphs, and modern prompts.

Install a Nerd Font:

```bash
cd ~/Downloads
wget -O JetBrainsMono.zip "https://sourceforge.net/projects/nerd-fonts.mirror/files/v3.4.0/JetBrainsMono.zip/download"
unzip -o JetBrainsMono.zip -d JetBrainsMonoNF

mkdir -p ~/.local/share/fonts/JetBrainsMonoNerdFont
cp JetBrainsMonoNF/*.ttf ~/.local/share/fonts/JetBrainsMonoNerdFont/

fc-cache -fv
```

---

### ✨ Prompt — Starship

Fast cross-shell prompt with Git integration and powerline support.

**Install**

```bash
curl -sS https://starship.rs/install.sh | sh
```

**Enable (bash)**

Add to `~/.bashrc`:

```bash
eval "$(starship init bash)"
```

---

### 🎨 Starship Configuration (Tokyo Night-style block prompt)

```
~/.config/starship.toml
```

Example powerline configuration:

```toml
add_newline = false

format = """
[](#7aa2f7)\
$username\
[](bg:#7aa2f7 fg:#7aa2f7)\
$directory\
[](fg:#7aa2f7 bg:#bb9af7)\
$git_branch$git_status\
[](fg:#bb9af7)\
$os\
$character
"""

[username]
show_always = true
style_user = "bg:#7aa2f7 fg:#1a1b26"
format = "[$user]($style)"

[directory]
style = "bg:#7aa2f7 fg:#1a1b26"
format = "[ $path ]($style)"
truncation_length = 3

[git_branch]
symbol = " "
style = "bg:#bb9af7 fg:#1a1b26"
format = "[ $symbol$branch ]($style)"

[git_status]
style = "bg:#bb9af7 fg:#1a1b26"

[os]
disabled = false
style = "bg:#a3aed2 fg:#090c0c"
format = "[ $symbol ]($style)"

[os.symbols]
Ubuntu = ""

[character]
success_symbol = "[ ❯](bold green)"
error_symbol = "[ ❯](bold red)"

# Disable 
```
