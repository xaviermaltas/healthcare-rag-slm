# 🔄 Lifecycle Scripts

Scripts per gestionar el cicle de vida del sistema Healthcare RAG.

## Scripts Disponibles

### `bootstrap.sh`
Configuració inicial del sistema (executar només una vegada).

```bash
./scripts/lifecycle/bootstrap.sh
```

### `start.sh`
Aixecar el sistema (ús diari).

```bash
./scripts/lifecycle/start.sh
```

### `stop.sh`
Aturar el sistema.

```bash
./scripts/lifecycle/stop.sh
```

### `rebuild.sh`
Reconstruir imatges Docker després de canvis al codi.

```bash
./scripts/lifecycle/rebuild.sh
```

## Flux de Treball

1. **Primera vegada**: `bootstrap.sh`
2. **Ús diari**: `start.sh` → treballar → `stop.sh`
3. **Després de canvis**: `rebuild.sh`
