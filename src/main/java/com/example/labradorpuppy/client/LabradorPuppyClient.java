package com.example.labradorpuppy.client;

import com.example.labradorpuppy.ModEntities;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public class LabradorPuppyClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        EntityRendererRegistry.register(ModEntities.PUPPY, PuppyRenderer::new);
    }
}
