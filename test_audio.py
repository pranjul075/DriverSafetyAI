import pygame
import time

print("Starting audio test...")

pygame.mixer.init()

sound = pygame.mixer.Sound("audio/warning.wav")

print("Playing beep...")

sound.play()

time.sleep(2)

print("Done.")
