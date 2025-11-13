from collections import defaultdict
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
racial_stats_file = os.path.join(project_root, 'data', 'racialstats.json')
with open(racial_stats_file, 'r', encoding='utf-8') as f:
    racial_stats = json.load(f)

attunements = ["Flamecharm", "Frostdraw", "Thundercall", "Galebreathe", "Shadowcast", "Ironsing", "Bloodrend"]

playerStats = {
    "Race": "None",
    "PointsSpent": 0,
}

def merge_stats(*dict_args):
    result = defaultdict(int)
    for dictionary in dict_args:
        for key, value in dictionary.items():
            result[key] += value
    return dict(result)

MAXIMUM_REDUCTION = 25

def order(stats, player_stats):
    # Calculate the points spent so far in the build, excluding racial stats

    if 'base' in stats:
        stats = merge_stats(stats['weapon'], stats['attunement'],stats['base'])    

    for stat_name, value in stats.items():
        if stat_name in racial_stats[player_stats["Race"]]:
            value -= racial_stats[player_stats["Race"]][stat_name]
        player_stats["PointsSpent"] += value

    # Save the points spent so far as point_start
    points_start = player_stats["PointsSpent"]
    
    # Create a shallow copy of the current stats as pre-shrine
    preshrine_build = stats.copy()
    
    # Identify which stats are invested for the shrine
    affected_stats = []
    for stat_name, stat_value in stats.items():
        if stat_value > 0:
            if stat_name in racial_stats[player_stats["Race"]]:
                if racial_stats[player_stats["Race"]][stat_name] > 0:
                    if stat_value - racial_stats[player_stats["Race"]][stat_name] == 0:
                        continue  # Skip if stat - racialStat equals to 0 (not invested)
            affected_stats.append(stat_name)
                # Initial division of points to every affected stat
    for stat_name in stats.keys():
        if stat_name in affected_stats:
            stats[stat_name] = points_start / len(affected_stats)

    # Prepare for the bottlenecking step
    bottlenecked = []
    bottlenecked_divide_by = len(affected_stats)
    previous_stats = stats.copy()

    while True:
        bottlenecked_points = 0
        bottlenecked_stats = False

        for stat_name, stat_value in stats.items():
            # Only bottleneck non-attunement affected stats
            if stat_name not in attunements and stat_name in affected_stats:
                shrine_stat = preshrine_build[stat_name]

                if shrine_stat - stat_value > MAXIMUM_REDUCTION:
                    # Set the stat to preshrine value - MAXIMUM_REDUCTION
                    stats[stat_name] = shrine_stat - MAXIMUM_REDUCTION
                    # Add the difference to bottlenecked points
                    bottlenecked_points += stats[stat_name] - previous_stats[stat_name]
                    bottlenecked.append(stat_name)
                    bottlenecked_divide_by -= 1  # Reduce the division counter

        # Averaging out bottlenecked points
        for stat_name, stat_value in stats.items():
            if stat_name in affected_stats and stat_name not in bottlenecked:
                stats[stat_name] -= bottlenecked_points / bottlenecked_divide_by
                
                # Check if any stat reduction is still larger than 25
                if stat_name not in attunements:
                    if preshrine_build[stat_name] - stats[stat_name] > 25:
                        bottlenecked_stats = True

        previous_stats = stats.copy()
        
        # Exit loop if no bottlenecked stats
        if not bottlenecked_stats:
            break

    # Round down all the stats and refund extra points
    for stat_name in stats.keys():
        stats[stat_name] = int(stats[stat_name])  # Rounding down

    # Calculate points spent after shrine
    points_spent_after_shrine = 0
    for stat_name, value in stats.items():
        if stat_name in racial_stats[player_stats["Race"]]:
            value -= racial_stats[player_stats["Race"]][stat_name]
        points_spent_after_shrine += value

    # Calculate spare points
    spare_points = points_start - points_spent_after_shrine

    # Ensure spare points do not exceed the number of affected stats
    if spare_points > len(affected_stats):
        for stat_name in affected_stats:
            stats[stat_name] += 1

    return stats #, spare_points