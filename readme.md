# Auto Cloud Upload

Auto File Uploader is a lightweight event-based tool that automatically monitors and syncs selected files to a target folder. This is useful for keeping files up-to-date in cloud storage or other backup locations.

## Features

- **Real-time Monitoring**: Detects file changes and copies them to a target directory.
- **Simple UI**: Allows basic management and monitoring of synced files.
- **Context Menu Integration**: Easily add files to the sync list via right-click.
- **Scheduled "LOGON" Task**: Listens to system events and copies files when updated.
- **Simple Configuration**: Uses a JSON file for easy customization.

## Installation (Windows)

1. Run the installer script: `install.cmd`
2. Choose the destination folder
3. Click **Install**

### Installer Actions

The installer performs the following steps:

1. **Creates a configuration file** in `%LOCALAPPDATA%`.
2. **Adds a context menu item** for adding files to sync.
3. **Schedules a background task** that listens to system events and monitors changes.

## JSON Files

### Configuration File (`config.json`)

The `config.json` file is used to define the target folder and sync settings.

```json
{
  "target": "C:\\Path\\To\\Target",
  "postpone-period": 2
}
```

- `target`: The directory where files are copied.
- `postpone-period`(s): Delay period before copying modified files, preventing excessive updates.

### Data File (`data.json`)

This file keeps track of registered files for syncing.

- `name`: Output filename in the target folder (same extension as the original).
- `path`: Full path of the monitored file.
- `last-update`: Timestamp of the last successful sync.

## Usage

1. **Add Files to Sync**
   - Right-click on a file and select *Add to Auto File Uploader*.
2. **Modify Files**
   - Any registered file that is changed will be automatically copied to the target directory.
3. **Monitor Files**
   - Logs and sync status can be checked in the UI.

## Troubleshooting

- **Files not syncing?** Ensure the scheduled task is running.
- **Need to change the target folder?** Can be changed via `settings` in the UI or directly in `config.json`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
