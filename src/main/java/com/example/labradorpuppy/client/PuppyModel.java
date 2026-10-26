package com.example.labradorpuppy.client;

import com.example.labradorpuppy.entity.PuppyEntity;
import net.minecraft.client.render.entity.model.EntityModel;
import net.minecraft.client.render.RenderLayer;
import net.minecraft.client.render.VertexConsumer;
import net.minecraft.client.util.math.MatrixStack;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

/**
 * Entity model that draws the original (non-cuboid) puppy mesh. Every frame the pose is
 * computed by {@link PuppyPose}, the vertices are skinned on the CPU by {@link PuppyMesh}
 * and then emitted as quads (each triangle = a quad with a repeated last vertex).
 */
public class PuppyModel extends EntityModel<PuppyEntity> {
    private final PuppyMesh mesh = PuppyMesh.get();
    private final PuppyPose pose = new PuppyPose();
    private final Matrix4f[] world = new Matrix4f[PuppyPose.BONE_COUNT];
    private final float[] scratch = new float[PuppyPose.BONE_COUNT * 16];
    private final float[] outPos;
    private final float[] outNrm;

    public PuppyModel() {
        super(RenderLayer::getEntityCutoutNoCull);
        if (mesh.boneCount != PuppyPose.BONE_COUNT) {
            throw new IllegalStateException("Mesh has " + mesh.boneCount + " bones, expected " + PuppyPose.BONE_COUNT);
        }
        for (int i = 0; i < world.length; i++) {
            world[i] = new Matrix4f();
        }
        outPos = new float[mesh.vertexCount * 3];
        outNrm = new float[mesh.vertexCount * 3];
    }

    @Override
    public void setAngles(PuppyEntity entity, float limbAngle, float limbDistance,
                          float animationProgress, float headYaw, float headPitch) {
        pose.update(limbAngle, limbDistance, animationProgress, headYaw, headPitch);
        pose.computeWorld(mesh, world);
        mesh.skin(world, scratch, outPos, outNrm);
    }

    @Override
    public void render(MatrixStack matrices, VertexConsumer vertices, int light, int overlay,
                       float red, float green, float blue, float alpha) {
        MatrixStack.Entry entry = matrices.peek();
        Matrix4f mat = entry.getPositionMatrix();
        Matrix3f nrmMat = entry.getNormalMatrix();
        int r = (int) (red * 255f), g = (int) (green * 255f), b = (int) (blue * 255f), a = (int) (alpha * 255f);
        int[] tris = mesh.tris;
        for (int i = 0; i < tris.length; i += 3) {
            // a triangle is drawn as a degenerate quad: v0, v1, v2, v2
            emit(vertices, nrmMat, mat, tris[i], r, g, b, a, overlay, light);
            emit(vertices, nrmMat, mat, tris[i + 1], r, g, b, a, overlay, light);
            emit(vertices, nrmMat, mat, tris[i + 2], r, g, b, a, overlay, light);
            emit(vertices, nrmMat, mat, tris[i + 2], r, g, b, a, overlay, light);
        }
    }

    private void emit(VertexConsumer vc, Matrix3f nrmMat, Matrix4f mat, int v,
                      int r, int g, int b, int a, int overlay, int light) {
        vc.vertex(mat, outPos[v * 3], outPos[v * 3 + 1], outPos[v * 3 + 2])
                .color(r, g, b, a)
                .texture(mesh.uv[v * 2], mesh.uv[v * 2 + 1])
                .overlay(overlay)
                .light(light)
                .normal(nrmMat, outNrm[v * 3], outNrm[v * 3 + 1], outNrm[v * 3 + 2])
                .next();
    }
}
