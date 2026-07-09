# Introducing dotsync: One Command, All Your Machines

If you've ever set up a new laptop and spent an afternoon hunting down your `.zshrc`, `.vimrc`, and a dozen other config files scattered across old backups, you already know the problem. Dotfiles are small, but keeping them consistent across machines is a chore nobody enjoys.

That's why we built **dotsync** — a lightweight CLI tool that keeps your configuration files in sync across every machine you work on.

## How it works

dotsync treats your dotfiles like any other versioned project. Point it at a directory, and it tracks changes, pushes them to a remote of your choice (Git-based, so you already know how to use it), and pulls them down on any other machine with a single command:

```
dotsync init
dotsync add ~/.zshrc ~/.gitconfig ~/.config/nvim
dotsync push
```

On a new machine:

```
dotsync pull
```

That's it. Your shell aliases, editor settings, and tool configs show up exactly as you left them.

## What makes it different

- **No lock-in on storage.** Use your own Git remote — GitHub, GitLab, a self-hosted server, whatever you already trust.
- **Symlink-aware.** dotsync manages symlinks under the hood, so your original file locations stay untouched and editable.
- **Conflict-safe.** Before overwriting anything, dotsync shows you a diff and asks for confirmation — no silent overwrites.
- **Fast and dependency-light.** A single binary, no runtime dependencies, works the same on macOS and Linux.

## Why we built it

We got tired of ad-hoc symlink scripts and half-finished bash aliases that broke the moment we switched machines. dotsync is the tool we wanted for ourselves: boring, predictable, and easy to trust with the files that make your terminal feel like home.

Give it a try, and let us know what you think. Your setup, everywhere you go.
