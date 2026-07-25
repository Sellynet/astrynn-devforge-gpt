# Bloque 0 · Manifiesto de custodia de evidencia

Fecha de custodia: 2026-07-25

Repositorio: `Sellynet/astrynn-devforge-gpt`

Commit verificado: `e7cfb62f98f13ebde8fffb346ddefc40e549f1bd`

Merge commit en `main`: `816ad0383e8531f9ef14b1369e2065ac82a8de0b`

PR de consolidación técnica: `#45`

## Objeto

Este manifiesto registra la descarga y conservación fuera del almacenamiento temporal de GitHub Actions de los artifacts asociados al último commit del PR #45. Los ZIP originales fueron preservados sin modificación dentro del paquete externo `Aegis_Block0_Custody_2026-07-25.zip`.

SHA-256 del paquete externo: `d8a408de75558be6ceb6e2fea5c4f4ea79757467b7721e10b5177513eb82546a`.

## Workflows y artifacts

| Workflow | Run ID | Resultado | Artifact | Artifact ID | SHA-256 del ZIP | Expira en GitHub |
|---|---:|---|---|---:|---|---|
| CI | 30161831048 | `success` | No generó artifact | — | — | — |
| Block 0 Human Verification | 30161831038 | `success` | `block0-human-verification-14.zip` | 8620442018 | `bd9caa7457d67a85f8f336a6427e3962c30eeeeea98acf1952ad317ab0c5347c` | 2026-08-24 14:32:45 UTC |
| Block 0 Deliberate Negative Verification | 30161831062 | `success` | `block0-negative-verification-14.zip` | 8620441979 | `4d4ebb341eb33198b6b9701f16b08bd362d3f3a72fccf5ca54fb9f668d342b0a` | 2026-08-24 14:32:45 UTC |
| Block 0 Remaining Endpoint Verification | 30161831040 | `success` | `block0-remaining-endpoints-15.zip` | 8620442101 | `57567af24140c5d7a2c9d7850b6e18eda51b474f471b0b89a82ec9631386b69d` | 2026-08-24 14:32:46 UTC |
| Block 0 README Clean-room Verification | 30161831041 | `success` | `block0-readme-cleanroom-9.zip` | 8620442655 | `8646b97fea959b4b40650559732c7f4857e8b0924a49408acfadc173ea7ab528` | 2026-08-24 14:32:50 UTC |
| Block 0 Restart Persistence Verification | 30161831047 | `success` | `block0-restart-persistence-15.zip` | 8620442943 | `96275a424deefa3fdf72139a45645c15ae756b2ee0a39dceaa3ef436f8138365` | 2026-08-24 14:32:51 UTC |

## Validación de integridad

Los cinco SHA-256 calculados sobre los ZIP descargados coinciden exactamente con los digests publicados por GitHub Actions.

## Contenido preservado

- resultados humanos y automatizados de endpoints;
- controles negativos deliberados;
- ejecución clean-room extraída del README;
- evidencia de persistencia tras reinicio, incluida base SQLite sintética y su hash;
- logs de instalación, Ruff, pytest y Uvicorn;
- metadata de entorno.

## Seguridad de los datos

El material se generó con datos y credenciales sintéticos de desarrollo. Un escaneo básico del paquete no detectó patrones comunes de secretos reales. Esto no equivale a una auditoría profesional de secretos.

## Regla de custodia

Conservar el paquete íntegro, junto con su SHA-256, en almacenamiento durable con control de acceso y copia de seguridad. No depender de la retención temporal de GitHub Actions.

## Clasificación

`B0-C4 COMPLETADO · ARTIFACTS PRESERVADOS Y HASHES REGISTRADOS`
