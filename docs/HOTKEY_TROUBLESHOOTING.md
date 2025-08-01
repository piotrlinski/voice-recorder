# Hotkey Troubleshooting Guide

If hotkeys are not working in the Voice Recorder application, follow these steps:

## 1. Check macOS Accessibility Permissions

The most common cause of hotkey issues on macOS is missing accessibility permissions:

1. Go to **System Preferences** > **Security & Privacy** > **Privacy** > **Accessibility**
2. Click the lock icon to make changes (enter your password)
3. Add your terminal application (Terminal, iTerm2, etc.) to the list
4. If running from an IDE, also add the IDE to the list
5. Restart the application

## 2. Test Hotkey Detection

Run the debug script to test if keys are being detected:

```bash
python3 debug_hotkeys.py
```

Press the Right Shift key and see if it's detected. If you see output like:
```
Key pressed: Key.shift_r (type: <enum 'Key'>)
  Name: 'shift_r'
```
Then the key detection is working.

## 3. Use Manual Recording Button

If hotkeys still don't work, you can use the manual recording button in the GUI:

1. Open the Voice Recorder GUI application
2. Click the "🎤 Start Recording" button to start recording
3. Click the "⏹️ Stop Recording" button to stop recording

## 4. Check Configuration

Verify your hotkey configuration:

```bash
cat ~/.voicerecorder/config.ini
```

The hotkey should be set to `shift_r` for Right Shift key.

## 5. Alternative Hotkeys

If Right Shift doesn't work, try changing the hotkey in the configuration:

```ini
[hotkey]
key = shift_l
description = Left Shift key
```

Or try a different key like:
- `ctrl` (Control key)
- `alt` (Option key)
- `cmd` (Command key)

## 6. Debug Information

The application now includes debug logging. Look for messages like:
- "Key pressed: Key.shift_r"
- "Key match: True"
- "Recording started"

## 7. Common Issues

### Issue: No key detection at all
**Solution**: Check macOS accessibility permissions (Step 1)

### Issue: Keys detected but recording doesn't start
**Solution**: Check the configuration file and ensure the key name matches

### Issue: Recording starts but doesn't stop
**Solution**: This might be a timing issue. Try pressing the key more deliberately

## 8. Getting Help

If you're still having issues:

1. Run the debug script and share the output
2. Check the console output for error messages
3. Try the manual recording button as a workaround
4. Report the issue with details about your macOS version and setup

## 9. Manual Testing

To test the hotkey detection logic:

```bash
python3 test_hotkey_detection.py
```

This will verify that the key matching logic is working correctly. 