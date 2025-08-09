# Enhanced Pickaxe Function
# This function runs continuously to enhance pickaxe behavior

# Give players with pickaxes haste effect for faster mining
effect @a[hasitem={item=wooden_pickaxe}] haste 2 1
effect @a[hasitem={item=stone_pickaxe}] haste 2 2  
effect @a[hasitem={item=iron_pickaxe}] haste 2 3
effect @a[hasitem={item=golden_pickaxe}] haste 2 4
effect @a[hasitem={item=diamond_pickaxe}] haste 2 3
effect @a[hasitem={item=netherite_pickaxe}] haste 2 4

# Send a title message when first holding an enhanced pickaxe
title @a[hasitem={item=wooden_pickaxe}] actionbar Enhanced Wooden Pickaxe (Haste II)
title @a[hasitem={item=stone_pickaxe}] actionbar Enhanced Stone Pickaxe (Haste II)
title @a[hasitem={item=iron_pickaxe}] actionbar Enhanced Iron Pickaxe (Haste III) 
title @a[hasitem={item=golden_pickaxe}] actionbar Enhanced Golden Pickaxe (Haste IV)
title @a[hasitem={item=diamond_pickaxe}] actionbar Enhanced Diamond Pickaxe (Haste III)
title @a[hasitem={item=netherite_pickaxe}] actionbar Enhanced Netherite Pickaxe (Haste IV)