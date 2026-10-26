package com.example.labradorpuppy.client;

import com.example.labradorpuppy.LabradorPuppyMod;
import com.example.labradorpuppy.entity.PuppyEntity;
import net.minecraft.client.render.entity.EntityRendererFactory;
import net.minecraft.client.render.entity.MobEntityRenderer;
import net.minecraft.util.Identifier;

public class PuppyRenderer extends MobEntityRenderer<PuppyEntity, PuppyModel> {
    private static final Identifier TEXTURE =
            new Identifier(LabradorPuppyMod.MOD_ID, "textures/entity/labrador_puppy.png");

    public PuppyRenderer(EntityRendererFactory.Context context) {
        super(context, new PuppyModel(), 0.3f);
    }

    @Override
    public Identifier getTexture(PuppyEntity entity) {
        return TEXTURE;
    }
}
