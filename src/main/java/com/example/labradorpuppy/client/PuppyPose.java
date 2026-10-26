package com.example.labradorpuppy.client;

import org.joml.Matrix4f;

/**
 * Procedural IDLE + WALK animation for the puppy skeleton.
 *
 * Everything is a pure function of (limbAngle, limbDistance, age) which Minecraft already
 * provides to every model, so the animation is automatically in sync with the real movement:
 *   limbDistance ~ 0  -> IDLE  (breathing, head sway, tail wag, ear twitch)
 *   limbDistance ~ 1  -> WALK  (diagonal trot, knee flex, body bob, faster tail, bouncing ears)
 * and the two are blended smoothly while the puppy starts/stops.
 *
 * Tweak the constants below to change the feel of the animation.
 */
public final class PuppyPose {
    // Bone indices - same order as in tools/rig.py (BONES)
    public static final int BODY = 0, HEAD = 1, EAR_L = 2, EAR_R = 3, TAIL1 = 4, TAIL2 = 5,
            FL_UP = 6, FL_LOW = 7, FR_UP = 8, FR_LOW = 9, BL_UP = 10, BL_LOW = 11, BR_UP = 12, BR_LOW = 13;
    public static final int BONE_COUNT = 14;

    // ---- tweakables --------------------------------------------------------------------------
    static final double STRIDE_SPEED = 0.8;     // leg cycle speed relative to limbAngle
    static final double LEG_SWING = 0.62;       // rad, upper-leg swing at full speed
    static final double KNEE_FLEX = 0.85;       // rad, lower-leg fold while the leg moves forward
    static final double BODY_BOB = 0.022;       // blocks
    static final double TAIL_WAG_HZ = 2.2;
    static final double TAIL_WAG_IDLE = 0.30;   // rad
    static final double TAIL_WAG_WALK = 0.60;   // rad
    static final double BREATH_PERIOD_S = 2.8;
    // -----------------------------------------------------------------------------------------

    private static final double TWO_PI = Math.PI * 2.0;

    private final float[] t = new float[BONE_COUNT * 3];   // translation (blocks)
    private final float[] r = new float[BONE_COUNT * 3];   // rotation x,y,z (rad)
    private final float[] s = new float[BONE_COUNT * 3];   // scale
    private final Matrix4f local = new Matrix4f();

    private void rot(int bone, double rx, double ry, double rz) {
        r[bone * 3] = (float) rx;
        r[bone * 3 + 1] = (float) ry;
        r[bone * 3 + 2] = (float) rz;
    }

    private static double clamp(double v, double lo, double hi) {
        return v < lo ? lo : Math.min(v, hi);
    }

    public void update(float limbAngle, float limbDistance, float age, float headYawDeg, float headPitchDeg) {
        java.util.Arrays.fill(t, 0f);
        java.util.Arrays.fill(r, 0f);
        java.util.Arrays.fill(s, 1f);

        final double D = clamp(limbDistance, 0, 1);
        final double idle = 1.0 - D;
        final double ts = age / 20.0;
        final double phi = limbAngle * STRIDE_SPEED;
        final double sinPhi = Math.sin(phi), cosPhi = Math.cos(phi), sin2Phi = Math.sin(2 * phi);
        final double breath = Math.sin(ts * TWO_PI / BREATH_PERIOD_S);

        // --- body: bob / roll / wiggle while walking, breathing while idle
        t[BODY * 3 + 1] = (float) (-BODY_BOB * D * Math.abs(cosPhi));
        rot(BODY, 0.03 * D * sin2Phi, 0.05 * D * cosPhi, 0.04 * D * sinPhi);
        s[BODY * 3] = (float) (1 - 0.012 * breath * idle);
        s[BODY * 3 + 1] = (float) (1 + 0.030 * breath * idle);
        s[BODY * 3 + 2] = (float) (1 - 0.012 * breath * idle);

        // --- legs: trot (front-left + back-right move together)
        final double A = LEG_SWING * D, K = KNEE_FLEX * D;
        final double pA = phi, pB = phi + Math.PI;
        rot(FL_UP, A * Math.cos(pA), 0, 0);
        rot(BR_UP, A * Math.cos(pA), 0, 0);
        rot(FR_UP, A * Math.cos(pB), 0, 0);
        rot(BL_UP, A * Math.cos(pB), 0, 0);
        rot(FL_LOW, K * Math.max(0.0, Math.sin(pA)) + 0.08 * D, 0, 0);
        rot(BR_LOW, K * Math.max(0.0, Math.sin(pA)) + 0.08 * D, 0, 0);
        rot(FR_LOW, K * Math.max(0.0, Math.sin(pB)) + 0.08 * D, 0, 0);
        rot(BL_LOW, K * Math.max(0.0, Math.sin(pB)) + 0.08 * D, 0, 0);

        // --- head: follows where the entity looks + idle sway + walk bob
        final double yaw = clamp(Math.toRadians(headYawDeg), -1.05, 1.05) + 0.14 * Math.sin(ts * 0.9) * idle;
        final double pitch = clamp(Math.toRadians(headPitchDeg), -0.7, 0.7)
                + 0.035 * Math.sin(ts * 1.7) * idle + 0.03 * breath * idle + 0.05 * D * sin2Phi;
        rot(HEAD, pitch, yaw, -0.04 * D * sinPhi);

        // --- tail: always wagging, harder while walking, held a bit higher
        final double wagPhase = ts * TWO_PI * TAIL_WAG_HZ;
        final double amp = TAIL_WAG_IDLE + (TAIL_WAG_WALK - TAIL_WAG_IDLE) * D;
        rot(TAIL1, 0.15 + 0.20 * D + 0.04 * Math.sin(ts * 1.3), amp * Math.sin(wagPhase), 0);
        rot(TAIL2, 0.10 * D, amp * 0.9 * Math.sin(wagPhase - 0.9), 0);

        // --- ears: gentle sway, random-looking twitches, bounce when walking
        final double twitchL = Math.pow(Math.max(0.0, Math.sin(ts * 0.7)), 12) * 0.30;
        final double twitchR = Math.pow(Math.max(0.0, Math.sin(ts * 0.7 + 2.0)), 12) * 0.30;
        final double bounce = 0.14 * D * Math.sin(2 * phi + 0.6);
        rot(EAR_L, bounce + 0.04 * Math.sin(ts * 1.3), 0, 0.06 * Math.sin(ts * 2.1) + twitchL);
        rot(EAR_R, bounce + 0.04 * Math.sin(ts * 1.3 + 1.0), 0, -0.06 * Math.sin(ts * 2.1 + 1.0) - twitchR);
    }

    /** Builds the world matrix of every bone from the current pose (parents first). */
    public void computeWorld(PuppyMesh mesh, Matrix4f[] world) {
        for (int i = 0; i < BONE_COUNT; i++) {
            float px = mesh.pivot[i * 3], py = mesh.pivot[i * 3 + 1], pz = mesh.pivot[i * 3 + 2];
            local.identity()
                    .translate(t[i * 3], t[i * 3 + 1], t[i * 3 + 2])
                    .translate(px, py, pz)
                    .rotateZ(r[i * 3 + 2]).rotateY(r[i * 3 + 1]).rotateX(r[i * 3])
                    .scale(s[i * 3], s[i * 3 + 1], s[i * 3 + 2])
                    .translate(-px, -py, -pz);
            int parent = mesh.boneParent[i];
            if (parent < 0) {
                world[i].set(local);
            } else {
                world[parent].mul(local, world[i]);
            }
        }
    }
}
