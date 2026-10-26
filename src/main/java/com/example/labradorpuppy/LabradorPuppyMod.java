package com.example.labradorpuppy;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LabradorPuppyMod implements ModInitializer {
    public static final String MOD_ID = "labrador_puppy";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        ModEntities.init();
        ModItems.init();
        LOGGER.info("Labrador Puppy loaded!");
    }
}
