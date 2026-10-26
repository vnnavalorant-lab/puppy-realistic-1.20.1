package com.example.labradorpuppy;

import com.example.labradorpuppy.entity.PuppyEntity;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricEntityTypeBuilder;
import net.minecraft.entity.EntityDimensions;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.SpawnGroup;
import net.minecraft.entity.SpawnRestriction;
import net.minecraft.entity.passive.AnimalEntity;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;
import net.minecraft.world.Heightmap;
import net.minecraft.world.biome.BiomeKeys;

public final class ModEntities {
    private ModEntities() {}

    /** Entity id: labrador_puppy:puppy  (use /summon labrador_puppy:puppy) */
    public static final EntityType<PuppyEntity> PUPPY = Registry.register(
            Registries.ENTITY_TYPE,
            new Identifier(LabradorPuppyMod.MOD_ID, "puppy"),
            buildPuppyType());

    private static EntityType<PuppyEntity> buildPuppyType() {
        FabricEntityTypeBuilder.Mob<PuppyEntity> builder = FabricEntityTypeBuilder.createMob();
        builder.spawnGroup(SpawnGroup.CREATURE);
        builder.entityFactory(PuppyEntity::new);
        builder.dimensions(EntityDimensions.fixed(0.5f, 0.65f));
        builder.trackRangeBlocks(64);
        // Natural spawning rules (remove this line if you only want the spawn egg / /summon)
        builder.spawnRestriction(SpawnRestriction.Location.ON_GROUND,
                Heightmap.Type.MOTION_BLOCKING_NO_LEAVES, AnimalEntity::isValidNaturalSpawn);
        return builder.build();
    }

    public static void init() {
        FabricDefaultAttributeRegistry.register(PUPPY, PuppyEntity.createPuppyAttributes());

        // Natural spawning in biomes (the spawn rules live in buildPuppyType())
        BiomeModifications.addSpawn(
                BiomeSelectors.includeByKey(BiomeKeys.PLAINS, BiomeKeys.SUNFLOWER_PLAINS,
                        BiomeKeys.MEADOW, BiomeKeys.FOREST),
                SpawnGroup.CREATURE, PUPPY, 6, 2, 4);
    }
}
