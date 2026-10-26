package com.example.labradorpuppy;

import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.item.Item;
import net.minecraft.item.ItemGroups;
import net.minecraft.item.SpawnEggItem;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;

public final class ModItems {
    private ModItems() {}

    public static final Item PUPPY_SPAWN_EGG = Registry.register(
            Registries.ITEM,
            new Identifier(LabradorPuppyMod.MOD_ID, "puppy_spawn_egg"),
            new SpawnEggItem(ModEntities.PUPPY, 0xEBDCC0, 0x8A6A45, new Item.Settings()));

    public static void init() {
        ItemGroupEvents.modifyEntriesEvent(ItemGroups.SPAWN_EGGS)
                .register(entries -> entries.add(PUPPY_SPAWN_EGG));
    }
}
