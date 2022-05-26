# import the modules
import Leap, sys, thread, time, pygame

stemValues = {"bass": 0,
              "drums": 1,
              "melody": 2,
              "vocals": 3}

class Track():

    def __init__(self, song):
        self.volume = [0.0, 0.0, 0.0, 0.0]
        self.muted = [False, False, False, False]
        self.stems = {"bass": pygame.mixer.Sound("samples/" + song + "Bass.ogg"),
                      "drums": pygame.mixer.Sound("samples/" + song + "Drums.ogg"),
                      "melody": pygame.mixer.Sound("samples/" + song + "Melody.ogg"),
                      "vocals": pygame.mixer.Sound("samples/" + song + "Vocals.ogg")}
        self.channels = []


    def playAll(self):
        for stem in self.stems.values():
            self.channels.append(pygame.mixer.Sound.play(stem))

    def playStem(self, stem):
        pygame.mixer.Sound.play(self.stems[stem])

    def setVolume(self, volume):
        self.volume = [max(min(1.0, volume), 0.0), max(min(1.0, volume), 0.0), max(min(1.0, volume), 0.0),
                       max(min(1.0, volume), 0.0)]
        for stem in self.stems.values():
            pygame.mixer.Sound.set_volume(stem, self.volume[0])

    def setVolumeStem(self, volume, stem):
        self.volume[stemValues[stem]] = max(min(1.0, volume), 0.0)
        if not self.muted[stemValues[stem]]:
            pygame.mixer.Sound.set_volume(self.stems[stem], self.volume[stemValues[stem]])

    def toggleMuteStem(self, stem):
        if self.muted[stemValues[stem]]:
            pygame.mixer.Sound.set_volume(self.stems[stem], self.volume[stemValues[stem]])
            print"unmuted " + stem
            self.muted[stemValues[stem]] = False
        else:
            pygame.mixer.Sound.set_volume(self.stems[stem], 0.0)
            print"muted " + stem
            self.muted[stemValues[stem]] = True

    def unmuteStem(self, stem):
        pygame.mixer.Sound.set_volume(self.stems[stem], self.volume)

    def stopAll(self):
        for stem in self.stems.values():
            pygame.mixer.Sound.stop(stem)


def main():
    # initialize pygame and leapmotion controller
    pygame.init()
    pygame.mixer.set_num_channels(10)

    controller = Leap.Controller()
    controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
    controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
    controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
    controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
    #controller.config.set("Gesture.KeyTap.MinDownVelocity", 20.0)
    #controller.config.set("Gesture.KeyTap.HistorySeconds", .2)
    #controller.config.set("Gesture.KeyTap.MinDistance", 0.8)
    controller.config.set("Gesture.Circle.MinRadius", 15.0)
    controller.config.set("Gesture.Circle.MinArc", 10.5)
    controller.config.save()
    # load and set pygame modules
    pygame.display.set_caption("Gesture DJ")
    screen = pygame.display.set_mode((240, 180))
    # runtime clock
    clock = pygame.time.Clock()

    # load audio files for mixing
    track1 = Track("PG-118bpm-")
    track1.playAll()
    track1.setVolume(0.0)
    track2 = Track("HCANE-160bpm-")
    track2.playAll()
    track2.setVolume(0.0)
    track3 = Track("OTG-133bpm_138bpm_carti-")
    track4 = Track("JAILP2110bpm-")

    stemValues = {"bass": 0,
                  "drums": 1,
                  "melody": 2,
                  "vocals": 3}
    leftTracklist = [track1, track3]
    rightTracklist = [track2, track4]
    leftIndex = 0
    rightIndex = 0
    liveTracks = {
        "Left": track1,
        "Right": track2
    }

    print track2.stems.values()
    print track1.stems.values()
    print track1.channels
    # define a variable to control the main loop
    rotationCooldown = 0
    running = True
    # main loop
    while running:
        clock.tick(120)

        # get a new tracking frame
        frame = controller.frame()
        previousFrame = controller.frame(1)
        # process the frame

        # get hands
        for hand in frame.hands:

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
            pinch = hand.pinch_strength
            side = ""
            if hand.is_left:
                side = "Left"
            else:
                side = "Right"
            if hand.pinch_strength == 1:
                panning = (hand.palm_position.normalized).x
                panning += 0.9
                panning = panning / 2.0
                if panning < 0:
                    panning=0
                print panning
                right = panning
                left = 1 - right
                print "Left: " + str(left) + " Right: " + str(right)
                for channel in liveTracks[side].channels:
                    channel.set_volume(left, right)
            if hand.grab_strength == 1:
                for channel in liveTracks[side].channels:
                    channel.set_volume(0)
            previousHands = []
            for prevhand in previousFrame.hands:
                previousHands.append(prevhand.id)
            if hand.grab_strength < 1 and (hand.id in previousHands):
                if previousFrame.hand(hand.id).grab_strength > 0.9:
                    for channel in liveTracks[side].channels:
                        channel.set_volume(1)

            if rotationCooldown > 0:
                rotationCooldown -= 1
            if hand.rotation_probability(previousFrame) == 1 and rotationCooldown == 0 and abs(normal.roll * Leap.RAD_TO_DEG) > 100:
                rotationCooldown = 100
                print "rotation registered"
                liveTracks[side].stopAll()
                if side == "Right":
                    rightIndex += 1
                    if rightIndex > len(rightTracklist) - 1:
                        rightIndex = 0
                    liveTracks[side] = rightTracklist[rightIndex]
                    liveTracks[side].playAll()
                if side == "Left":
                    leftIndex += 1
                    if leftIndex > len(leftTracklist) - 1:
                        leftIndex = 0
                    liveTracks[side] = leftTracklist[leftIndex]
                    liveTracks[side].playAll()



            # Calculate the hand's pitch, roll, and yaw angles
            #print ("  pitch: %f degrees, roll: %f degrees, yaw: %f degrees") % (
                #    direction.pitch * Leap.RAD_TO_DEG,
                #    normal.roll * Leap.RAD_TO_DEG,
            #    direction.yaw * Leap.RAD_TO_DEG)

            # Get arm bone
            arm = hand.arm
            # print ("  Arm direction: %s, wrist position: %s, elbow position: %s") % (
            #    arm.direction,
            #    arm.wrist_position,
            #    arm.elbow_position)

            # get fingers

            left_fingers = []
            right_fingers = []
            for finger in hand.fingers:
                if hand.is_left:
                    left_fingers.append(finger.id)
                else:
                    right_fingers.append(finger.id)

            # find gestures
            for gesture in frame.gestures():
                if gesture.is_valid:

                    if gesture.type is Leap.Gesture.TYPE_SWIPE:
                        swipe = Leap.SwipeGesture(gesture)
                        ids = []
                        for prevgesture in previousFrame.gestures():
                            ids.append(prevgesture.id)
                        if gesture.id not in ids:
                            print "swipe registered"

                    if gesture.type is Leap.Gesture.TYPE_CIRCLE:
                        print "circle registered"
                        # process a circle gesture
                        circle = Leap.CircleGesture(gesture)
                        finger = Leap.Finger(circle.pointable)
                        # figure out which hand is gesturing
                        side = ""
                        circling = False
                        individualMode = True
                        if finger.id in right_fingers:
                            side = "Right"
                            circling = True
                        if finger.id in left_fingers:
                            side = "Left"
                            circling = True
                        # figure out which finger is gesturing
                        # finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                        finger_names = ["bass", "melody", "drums", "drums", "vocals"]
                        fingerStem = finger_names[finger.type]

                        if circling and circle.radius > 20.0:
                            # find direction of circle
                            if (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI / 2):
                                clockwiseness = "clockwise"
                                if not individualMode:
                                    liveTracks[side].setVolume(liveTracks[side].volume + circle.progress / 30)
                                else:
                                    liveTracks[side].setVolumeStem(
                                        liveTracks[side].volume[stemValues[fingerStem]] + circle.progress / 30,
                                        fingerStem)
                            else:
                                clockwiseness = "counterclockwise"
                                if not individualMode:
                                    liveTracks[side].setVolume(liveTracks[side].volume - circle.progress / 30)
                                else:
                                    liveTracks[side].setVolumeStem(
                                        liveTracks[side].volume[stemValues[fingerStem]] - circle.progress / 30,
                                        fingerStem)

                            print "Right volume: " + str(liveTracks["Right"].volume)
                            print "Left volume: " + str(liveTracks["Left"].volume)

                    #if gesture.type is Leap.Gesture.TYPE_SCREEN_TAP:
                    #    print "screen tap registered"
                    #    screen_tap = Leap.ScreenTapGesture(gesture)
                    #    finger = Leap.Finger(screen_tap.pointable)
                    #    # figure out which hand is gesturing
                    #    side = ""
                    #    if finger.id in right_fingers:
                    #        side = "Right"
                    #    if finger.id in left_fingers:
                    #        side = "Left"
                        # figure out which finger is gesturing
                        # finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']

                            #    if side != "":
                            #         finger_names = ["bass", "melody", "drums", "drums", "vocals"]
                            #fingerStem = finger_names[finger.type]
                            #liveTracks[side].toggleMuteStem(fingerStem)
                    if gesture.type is Leap.Gesture.TYPE_KEY_TAP:
                        ids = []
                        for prevgesture in previousFrame.gestures():
                            ids.append(prevgesture.id)
                        if gesture.id not in ids:
                            print "key tap registered"
                            key_tap = Leap.KeyTapGesture(gesture)
                            finger = Leap.Finger(key_tap.pointable)
                            # figure out which hand is gesturing
                            side = ""
                            if finger.id in right_fingers:
                                side = "Right"
                            if finger.id in left_fingers:
                                side = "Left"
                            if side != "":
                                # figure out which finger is gesturing
                                # finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                                finger_names = ["bass", "melody", "drums", "bass", "vocals"]
                                fingerStem = finger_names[finger.type]
                                liveTracks[side].toggleMuteStem(fingerStem)


        # pygame event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False


if __name__ == "__main__":
    main()
