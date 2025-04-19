#!/usr/bin/env python3

import os
import time
import datetime
import subprocess
import signal
import sys
import argparse

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Dictionary mapping time components to audio filenames
# Note: Replace these with your actual filenames
AUDIO_FILES = {
    'intro': 'ekhon_somoy.wav',  # এখন সময়
    
    # Hours (with 'টা' already included)
    'hour_1': 'ekta.wav',        # একটা
    'hour_2': 'duita.wav',       # দুইটা
    'hour_3': 'tinta.wav',       # তিনটা
    'hour_4': 'charta.wav',      # চারটা
    'hour_5': 'panchta.wav',     # পাঁচটা
    'hour_6': 'choyta.wav',      # ছয়টা
    'hour_7': 'shatta.wav',      # সাতটা
    'hour_8': 'atta.wav',        # আটটা
    'hour_9': 'noyta.wav',       # নয়টা
    'hour_10': 'doshta.wav',     # দশটা
    'hour_11': 'egarota.wav',    # এগারোটা
    'hour_12': 'barota.wav',     # বারোটা
    
    # Minutes
    'minute_15': 'poner_minute.wav',  # পনের মিনিট
    'minute_30': 'trish_minute.wav',  # ত্রিশ মিনিট
    'minute_45': 'poytallish_minute.wav',  # পয়তাল্লিশ মিনিট
    
    # Time periods
    'period_dawn': 'bhor.wav',   # ভোর (dawn) - early morning
    'period_morning': 'sokal.wav',  # সকাল (morning)
    'period_noon': 'dupur.wav',   # দুপুর (noon/afternoon)
    'period_evening': 'bikal.wav',  # বিকাল (evening)
    'period_dusk': 'shondha.wav',  # সন্ধ্যা (dusk)
    'period_night': 'rat.wav',    # রাত (night)
}

# Path to your audio files directory
AUDIO_DIR = os.path.expanduser("~/time_announcer_audio")

# Time periods in Bangla
TIME_PERIODS = {
    # Dawn: 4 AM to 6 AM
    4: 'period_dawn', 5: 'period_dawn',
    # Morning: 6 AM to 11 AM
    6: 'period_morning', 7: 'period_morning', 8: 'period_morning', 
    9: 'period_morning', 10: 'period_morning', 11: 'period_morning',
    # Noon/Afternoon: 12 PM to 3 PM
    12: 'period_noon', 13: 'period_noon', 14: 'period_noon', 15: 'period_noon',
    # Evening: 4 PM to 5 PM
    16: 'period_evening', 17: 'period_evening',
    # Dusk: 6 PM to 7 PM
    18: 'period_dusk', 19: 'period_dusk',
    # Night: 8 PM to 3 AM
    20: 'period_night', 21: 'period_night', 22: 'period_night', 23: 'period_night',
    0: 'period_night', 1: 'period_night', 2: 'period_night', 3: 'period_night'
}

# Global variables
running = True

def get_audio_files_for_time():
    """Get the list of audio files needed to announce the current time"""
    now = datetime.datetime.now()
    hour_24 = now.hour
    hour_12 = now.hour % 12
    if hour_12 == 0:
        hour_12 = 12
    minute = now.minute
    
    # Round to the nearest interval
    if minute < 8:
        minute_rounded = 0
    elif minute < 23:
        minute_rounded = 15
    elif minute < 38:
        minute_rounded = 30
    elif minute < 53:
        minute_rounded = 45
    else:
        minute_rounded = 0
        hour_12 = (hour_12 % 12) + 1
        hour_24 = (hour_24 + 1) % 24
    
    # Create audio queue
    files = []
    
    # Sequence: "এখন সময়, [time period], [hour]টা, [minutes]"
    # Add intro - "এখন সময়"
    files.append(AUDIO_FILES['intro'])
    
    # Add time period (e.g., সকাল, দুপুর, etc.)
    files.append(AUDIO_FILES[TIME_PERIODS[hour_24]])
    
    # Add hour (with টা already included)
    files.append(AUDIO_FILES[f'hour_{hour_12}'])
    
    # Add minutes part if not on the hour
    if minute_rounded == 15:
        files.append(AUDIO_FILES['minute_15'])
    elif minute_rounded == 30:
        files.append(AUDIO_FILES['minute_30'])
    elif minute_rounded == 45:
        files.append(AUDIO_FILES['minute_45'])
    
    return files

def play_audio_sequence_pygame(audio_files):
    """Play a sequence of audio files using pygame"""
    pygame.mixer.init()
    
    for audio_file in audio_files:
        full_path = os.path.join(AUDIO_DIR, audio_file)
        if not os.path.exists(full_path):
            print(f"Warning: Audio file not found: {full_path}")
            continue
            
        try:
            sound = pygame.mixer.Sound(full_path)
            sound.play()
            # Wait for the audio to finish
            while pygame.mixer.get_busy():
                pygame.time.delay(100)
        except Exception as e:
            print(f"Error playing audio file {audio_file}: {e}")

def play_audio_sequence_aplay(audio_files):
    """Play a sequence of audio files using aplay"""
    for audio_file in audio_files:
        full_path = os.path.join(AUDIO_DIR, audio_file)
        if not os.path.exists(full_path):
            print(f"Warning: Audio file not found: {full_path}")
            continue
            
        try:
            subprocess.run(["aplay", full_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error playing audio file {audio_file}: {e}")

def announce_time():
    """Announce the current time using audio files"""
    now = datetime.datetime.now()
    print(f"[{now:%Y-%m-%d %H:%M:%S}] Announcing time...")
    
    audio_files = get_audio_files_for_time()
    
    if PYGAME_AVAILABLE:
        play_audio_sequence_pygame(audio_files)
    else:
        play_audio_sequence_aplay(audio_files)

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    global running
    print("\nStopping Bangla Time Announcer...")
    running = False

def check_audio_files():
    """Check if required audio files exist, return list of missing files"""
    missing_files = []
    
    if not os.path.exists(AUDIO_DIR):
        try:
            os.makedirs(AUDIO_DIR)
            print(f"Created audio directory: {AUDIO_DIR}")
        except Exception as e:
            print(f"Error creating audio directory: {e}")
            return list(AUDIO_FILES.values())
    
    for file_name in AUDIO_FILES.values():
        file_path = os.path.join(AUDIO_DIR, file_name)
        if not os.path.exists(file_path):
            missing_files.append(file_name)
            
    return missing_files

def run_announcer(interval=30, test_only=False):
    """Main function to run the time announcer"""
    global running
    
    # Check if pygame is available, otherwise try to use aplay
    if not PYGAME_AVAILABLE:
        print("Warning: pygame not found, trying to use aplay instead.")
        try:
            subprocess.run(["aplay", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print("Error: Neither pygame nor aplay is available. Cannot play audio.")
            print("Please install pygame (pip install pygame) or aplay (alsa-utils package).")
            return
    
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check for missing audio files
    missing_files = check_audio_files()
    if missing_files:
        print(f"Missing {len(missing_files)} audio files in {AUDIO_DIR}:")
        for file in missing_files[:10]:
            print(f"  - {file}")
        if len(missing_files) > 10:
            print(f"  ... and {len(missing_files) - 10} more.")
        print("\nPlease add these files to continue.")
        return
    
    # Test once if requested
    if test_only:
        announce_time()
        return
    
    print(f"Bangla Time Announcer started (announcing every {interval} minutes)")
    print(f"Audio files directory: {AUDIO_DIR}")
    print("Press Ctrl+C to stop")
    
    # Announce once at startup
    announce_time()
    
    # Main loop
    while running:
        now = datetime.datetime.now()
        
        # Calculate time until next announcement
        if interval == 15:
            # Every 15 minutes (XX:00, XX:15, XX:30, XX:45)
            next_minute = ((now.minute // 15) + 1) * 15
            if next_minute == 60:
                next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            else:
                next_time = now.replace(minute=next_minute, second=0, microsecond=0)
        elif interval == 30:
            # Every 30 minutes (XX:00, XX:30)
            if now.minute < 30:
                next_time = now.replace(minute=30, second=0, microsecond=0)
            else:
                next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        else:  # interval == 60
            # Every hour (XX:00)
            next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        
        # Wait until next announcement time
        wait_seconds = (next_time - now).total_seconds()
        
        while wait_seconds > 0 and running:
            # Sleep in smaller chunks to be responsive to Ctrl+C
            sleep_time = min(wait_seconds, 10)
            time.sleep(sleep_time)
            wait_seconds -= sleep_time
            if not running:
                break
        
        # If we're still running, announce the time
        if running:
            announce_time()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bangla Time Announcer")
    parser.add_argument("--interval", type=int, choices=[15, 30, 60], default=30,
                        help="Announcement interval in minutes (15, 30, or 60)")
    parser.add_argument("--test", action="store_true", 
                        help="Test announcement once and exit")
    args = parser.parse_args()
    
    run_announcer(interval=args.interval, test_only=args.test)
