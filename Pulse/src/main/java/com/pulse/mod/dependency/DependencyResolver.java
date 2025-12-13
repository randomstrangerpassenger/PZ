
package com.pulse.mod.dependency;

import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModMetadata;
import com.pulse.mod.VersionComparator;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Handles dependency resolution and topological sorting of mods.
 */
public class DependencyResolver {
    private static final String LOG = PulseLogger.PULSE;
    private final Map<String, ModContainer> mods;

    public DependencyResolver(Map<String, ModContainer> mods) {
        this.mods = mods;
    }

    public List<ModContainer> resolve() {
        PulseLogger.info(LOG, "Resolving dependencies...");

        List<String> errors = checkDependenciesAndConflicts();
        if (!errors.isEmpty()) {
            PulseLogger.error(LOG, "Dependency/Conflict errors:");
            for (String error : errors) {
                PulseLogger.error(LOG, "  ✗ {}", error);
            }
        }

        List<ModContainer> loadOrder = performTopologicalSort();

        for (ModContainer container : loadOrder) {
            container.setState(ModContainer.ModState.DEPENDENCIES_RESOLVED);
        }

        PulseLogger.info(LOG, "Load order: {}",
                loadOrder.stream().map(ModContainer::getId).collect(Collectors.joining(" → ")));

        return loadOrder;
    }

    private List<String> checkDependenciesAndConflicts() {
        List<String> errors = new ArrayList<>();
        for (ModContainer container : mods.values()) {
            ModMetadata metadata = container.getMetadata();

            // Check Dependencies
            for (ModMetadata.Dependency dep : metadata.getDependencies()) {
                if ("Pulse".equals(dep.getId()))
                    continue;

                ModContainer depMod = mods.get(dep.getId());
                if (depMod == null) {
                    if (dep.isOptional()) {
                        PulseLogger.info(LOG, "  - {}: optional dependency '{}' not found",
                                metadata.getId(), dep.getId());
                    } else {
                        errors.add(metadata.getId() + " requires " + dep.getId() + " " + dep.getVersion());
                    }
                } else {
                    String actualVersion = depMod.getMetadata().getVersion();
                    String requiredVersion = dep.getVersion();
                    if (requiredVersion != null && !requiredVersion.isEmpty() && !"*".equals(requiredVersion)) {
                        if (VersionComparator.matches(actualVersion, requiredVersion)) {
                            PulseLogger.info(LOG, "  - {} → {} v{} ✓", metadata.getId(), dep.getId(), actualVersion);
                        } else {
                            errors.add(metadata.getId() + " requires " + dep.getId() + " " +
                                    requiredVersion + " but found " + actualVersion);
                        }
                    } else {
                        PulseLogger.info(LOG, "  - {} → {} v{} ✓", metadata.getId(), dep.getId(), actualVersion);
                    }
                }
            }

            // Check Conflicts
            for (String conflictId : metadata.getConflicts()) {
                if (mods.containsKey(conflictId)) {
                    errors.add(metadata.getId() + " conflicts with " + conflictId);
                    PulseLogger.error(LOG, "✗ Conflict detected: {} and {} cannot be loaded together",
                            metadata.getId(), conflictId);
                }
            }
        }
        return errors;
    }

    private List<ModContainer> performTopologicalSort() {
        List<ModContainer> result = new ArrayList<>();
        Set<String> visited = new HashSet<>();
        Set<String> visiting = new HashSet<>();

        for (String modId : mods.keySet()) {
            if (!visited.contains(modId)) {
                topologicalSort(modId, visited, visiting, result);
            }
        }
        return result;
    }

    private void topologicalSort(String modId, Set<String> visited, Set<String> visiting, List<ModContainer> result) {
        if (visited.contains(modId))
            return;
        if (visiting.contains(modId)) {
            PulseLogger.error(LOG, "Circular dependency detected: {}", modId);
            return;
        }

        visiting.add(modId);

        ModContainer container = mods.get(modId);
        if (container != null) {
            for (ModMetadata.Dependency dep : container.getMetadata().getDependencies()) {
                if (mods.containsKey(dep.getId())) {
                    topologicalSort(dep.getId(), visited, visiting, result);
                }
            }
            result.add(container);
        }

        visiting.remove(modId);
        visited.add(modId);
    }
}
