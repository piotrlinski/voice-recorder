# Voice Recorder Purge Command

## Overview

The `voice-recorder purge` command removes temporary voice files from the application's temp directory. This is useful for cleaning up disk space and removing old recordings.

## Usage

### Basic Usage

```bash
# Remove temporary voice files with confirmation
voice-recorder purge

# Force deletion without confirmation
voice-recorder purge --force

# Preview what would be deleted (dry run)
voice-recorder purge --dry-run
```

### Command Options

- `--force, -f`: Force deletion without confirmation
- `--dry-run, -n`: Show what would be deleted without actually deleting
- `--help`: Show help information

## Features

### File Detection

The purge command automatically detects and removes common audio file formats:
- `.wav` - Waveform Audio File Format
- `.mp3` - MPEG Audio Layer III
- `.flac` - Free Lossless Audio Codec
- `.m4a` - MPEG-4 Audio
- `.ogg` - Ogg Vorbis

### Safety Features

1. **Dry Run Mode**: Use `--dry-run` to preview what files would be deleted
2. **Confirmation Prompt**: By default, asks for confirmation before deleting
3. **File Information**: Shows file names and sizes before deletion
4. **Error Handling**: Continues deletion even if some files fail to delete
5. **Directory Check**: Verifies temp directory exists before proceeding

### Output Examples

#### Dry Run
```
📁 Found 3 temporary voice files:
   📄 recording_2024_01_15_14_30_22.wav (245760 bytes)
   📄 recording_2024_01_15_14_35_18.mp3 (189440 bytes)
   📄 recording_2024_01_15_14_40_05.flac (312320 bytes)
🔍 Dry run: Would delete 3 files
```

#### Confirmation Mode
```
📁 Found 3 temporary voice files:
   📄 recording_2024_01_15_14_30_22.wav (245760 bytes)
   📄 recording_2024_01_15_14_35_18.mp3 (189440 bytes)
   📄 recording_2024_01_15_14_40_05.flac (312320 bytes)
⚠️ About to delete 3 temporary voice files
Do you want to continue? [y/N]: y
🗑️ Deleted: recording_2024_01_15_14_30_22.wav
🗑️ Deleted: recording_2024_01_15_14_35_18.mp3
🗑️ Deleted: recording_2024_01_15_14_40_05.flac
╭──────────────── Purge Complete ─────────────────╮
│ ✅ Successfully deleted 3 temporary voice files │
╰─────────────────────────────────────────────────╯
```

#### Force Mode
```
📁 Found 3 temporary voice files:
   📄 recording_2024_01_15_14_30_22.wav (245760 bytes)
   📄 recording_2024_01_15_14_35_18.mp3 (189440 bytes)
   📄 recording_2024_01_15_14_40_05.flac (312320 bytes)
🗑️ Deleted: recording_2024_01_15_14_30_22.wav
🗑️ Deleted: recording_2024_01_15_14_35_18.mp3
🗑️ Deleted: recording_2024_01_15_14_40_05.flac
╭──────────────── Purge Complete ─────────────────╮
│ ✅ Successfully deleted 3 temporary voice files │
╰─────────────────────────────────────────────────╯
```

## Configuration

The purge command uses the temp directory specified in your configuration file (`~/.voicerecorder/config.json`). The default location is:

- **macOS/Linux**: `~/.voicerecorder/temp`
- **Windows**: `%USERPROFILE%\.voicerecorder\temp`

## Error Handling

The command handles various error conditions gracefully:

1. **Missing Temp Directory**: Shows warning and exits gracefully
2. **No Files Found**: Shows informative message
3. **Permission Errors**: Continues with other files, reports errors
4. **File Locked**: Reports error but continues with other files

## Integration with Other Commands

The purge command works seamlessly with other CLI commands:

```bash
# Check status and temp directory
voice-recorder status

# Clean up temp files
voice-recorder purge --dry-run

# If satisfied with preview, delete files
voice-recorder purge --force
```

## Best Practices

1. **Use Dry Run First**: Always run `--dry-run` to preview what will be deleted
2. **Regular Cleanup**: Run purge periodically to free up disk space
3. **Backup Important Files**: Move important recordings before purging
4. **Check Status**: Use `voice-recorder status` to verify temp directory location

## Technical Details

### Implementation

The purge command is implemented in `src/voice_recorder/cli/main.py` and includes:

- **File Pattern Matching**: Uses `pathlib.Path.glob()` for efficient file discovery
- **Rich Console Output**: Uses Rich library for beautiful terminal output
- **Error Recovery**: Continues processing even if individual files fail
- **Progress Reporting**: Shows detailed information about each file

### File Types Supported

The command recognizes these audio file extensions:
- `.wav` - Uncompressed audio (default recording format)
- `.mp3` - Compressed audio
- `.flac` - Lossless compressed audio
- `.m4a` - AAC audio in MP4 container
- `.ogg` - Ogg Vorbis compressed audio

### Performance

- **Fast Scanning**: Uses efficient file system operations
- **Memory Efficient**: Processes files one at a time
- **Parallel Safe**: Can be run while application is recording
- **Cross-Platform**: Works on macOS, Linux, and Windows 