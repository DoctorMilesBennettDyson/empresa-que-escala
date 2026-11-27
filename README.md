# Cómo se construye una empresa que escala

**Lo que Ford, Toyota, Apple, Amazon y SpaceX resolvieron con lápiz, y cualquiera puede rehacer: cinco cuentas, doce recetas y veintiséis lecciones de otras industrias.**

Un manual de principios, cuentas y recetas para diseñar, producir, vender y financiar un negocio que pueda crecer. Es para quien tiene o quiere tener un taller, un servicio, una fábrica, un comercio o un producto digital, y para quien lo enseña. Versión 2.0, octubre de 2026. Tiene 43 figuras.

## Leerlo

| Formato | Para qué | Archivo |
|---|---|---|
| Web | Leer en el navegador o en el celular, con índice | **https://doctormilesbennettdyson.github.io/empresa-que-escala/** |
| PDF A4 | Imprimir | [Como_se_construye_una_empresa_que_escala_v2.0.pdf](Como_se_construye_una_empresa_que_escala_v2.0.pdf) |
| PDF A5 | Leer en el celular o imprimir en formato libro | [Como_se_construye_una_empresa_que_escala_v2.0_A5.pdf](Como_se_construye_una_empresa_que_escala_v2.0_A5.pdf) |
| Láminas | Compartir una idea suelta: 43 imágenes de 1080×1350 px, una por figura | [laminas/](laminas/) |
| Texto fuente | Citar, adaptar o traducir | [MANUAL_EMPRESAS_QUE_ESCALAN.md](MANUAL_EMPRESAS_QUE_ESCALAN.md) |

## De dónde sale cada dato

Cada número del libro dice qué tan firme es: `[verificado, primaria/secundaria]`, `[reportado]`, `[cálculo]`, `[hipótesis]` o `[interpretación]`. El [registro de afirmaciones](REGISTRO_AFIRMACIONES_Manual.md) lista cada una con su fuente y su estado. Las figuras no agregan datos: todo lo que muestran sale del texto. Dos figuras son lecturas del autor y lo dicen dentro del dibujo, con la etiqueta `[interpretación]`. Una es la figura 3, sobre qué función cubría cada fundador de Apple. La otra es la figura 30, sobre en qué nivel se comete cada uno de los doce errores.

Si encontrás un error, abrí un *issue* con la página y la fuente.

## Rehacer las figuras, las láminas y la web

| Qué | Script | Necesita |
|---|---|---|
| Figuras SVG, apaisadas y verticales | `figuras/_generar_figuras.py` | Python 3.8 o más nuevo |
| Láminas PNG | `figuras/_generar_laminas.py` | Microsoft Edge (lo usa para dibujar el SVG) |
| Web | `_generar_web.py` + `_estilo_web.html` | pandoc |

Los PDF se arman con pandoc y las hojas de estilo `_estilo_*.html`. La herramienta que los convierte a PDF no está en este repositorio.

## Licencia y cita

Escrito por Claude (Anthropic) a pedido de Pablo Luciano Rainieri Blasco, que lo publica y no lo revisó entero (ver [AUTORIA.md](AUTORIA.md)). El texto, las figuras y las láminas tienen licencia [Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](LICENSE). Se pueden copiar, adaptar, traducir y redistribuir, también con fines comerciales, siempre que se cite al autor.

> Claude (Anthropic), a pedido de P. L. Rainieri Blasco (2026). *Cómo se construye una empresa que escala* (versión 2.0). CC BY 4.0. https://github.com/DoctorMilesBennettDyson/empresa-que-escala

---

*English summary.* This is a free, Spanish-language handbook (CC BY 4.0) on how firms scale. It works through five cases: Ford, Toyota, Apple, Amazon and SpaceX. From them it draws five calculations, twelve recipes and twenty-six lessons from aviation, defense, medicine, computing and logistics. Every figure in the book is tagged with how firm its evidence is. Read it on the web: https://doctormilesbennettdyson.github.io/empresa-que-escala/
