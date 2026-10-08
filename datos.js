// Base de datos viva y acumulativa de IPD
const baseDatosIPD = [
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución 682-MIYSPGP-2026",
    criollo: "El Estado crea un Fondo de Compensaciones Tarifarias que paga a los distribuidores municipales cuando sus costos superan los de referencia, pero la tarifa final que paga el usuario no baja. ¿A quién le sirve? A las empresas eléctricas, mientras el bolsillo del laburante sigue cargado. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Tarifas fijas para usuarios:</b> no baja el precio de la luz, se mantiene o sube.\n- <b>Beneficio a concesionarios eléctricos:</b> reciben compensación sin que el Estado asuma costos.\n- <b>Coste para los contribuyentes:</b> el fondo se financia con cargos obligatorios a los usuarios.",
    letraChica: "La compensación se financia con aportes obligatorios de los usuarios y sin control de gasto, permitiendo que los concesionarios recuperen costos extra sin inversión pública."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución 160/24",
    criollo: "El Estado destina casi 10 millones de pesos a la cooperativa Abriendo Caminos para comprar materia prima y equipamiento. ¿A quién le sirve? A esa empresa y a sus dueños, no al trabajador promedio. El dinero sale del erario, lo paga la gente y no hay garantía de que genere empleo masivo. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Finanzas públicas</b>: se asignan $9,9 M a una cooperativa, carga al erario y a los contribuyentes.\n- <b>Empleo</b>: el subsidio solo beneficia a la cooperativa, sin garantía de crear puestos para la mayoría.\n- <b>Transparencia</b>: la selección no es clara, favoreciendo a grupos vinculados al gobierno.",
    letraChica: "El anexo no detalla criterios de adjudicación ni mecanismos de rendición; el subsidio se otorga sin competencia, favoreciendo a la cooperativa elegida y dejando fuera a otras organizaciones."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución RESO-2021-943-GDEBA-MIYSPGP",
    criollo: "El Estado paga $1,176 M extra a la empresa constructora y la deja sin derecho a reclamar costos mayores. El gasto se carga al presupuesto provincial y a los contribuyentes, mientras el trabajador no recibe mejora ni empleo garantizado.",
    afecta: "- <b>Mayor gasto público:</b> +$1,176 M al presupuesto, recortando fondos de salud, educación y empleo.\n- <b>Beneficio a la empresa:</b> la contratista cobra +$1,176 M y renuncia a reclamos, sin asegurar nuevos puestos.\n- <b>Trabajador excluido:</b> no hay aumento de empleo ni mejora salarial; la carga recae en los laburantes vía impuestos.",
    letraChica: "La renuncia de la contratista a reclamar sobrecostos impide revisar futuros aumentos, garantizando que cualquier exceso recaiga totalmente sobre la provincia y, por ende, sobre los contribuyentes."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución 682/2026",
    criollo: "El Estado crea un Fondo Provincial de Compensaciones Tarifarias que paga a los distribuidores municipales cuando sus costos superan los de referencia. ¿Quién paga esa compensación? Los usuarios, entre ellos los laburantes, absorben el gasto en la factura de luz. Se promete igualdad tarifaria, pero la carga recae en el pueblo.",
    afecta: "<b>Tarifas eléctricas</b>: se mantienen o suben para cubrir compensaciones, encareciendo la luz del laburante.\n<b>Concesionarios</b>: reciben dinero del fondo sin que se demuestre mayor eficiencia, se benefician.",
    letraChica: "La resolución permite ajustes de alícuotas sin control estricto; los faltantes del fondo se cubren después con cargos a los usuarios, ocultando el verdadero costo al contribuyente."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "caba",
    titulo: "Resolución 696/2026",
    criollo: "La medida sube los precios de la licitación pública, encareciendo la obra para la Ciudad y enriqueciendo al empresario que la ejecutará. El gasto extra recae sobre el erario municipal, reduciendo recursos para salud, educación o salarios del sector público y pudiendo trasladarse a los contribuyentes.",
    afecta: "<b>Presupuesto municipal</b>: encarece la obra y reduce fondos disponibles.\n<b>Trabajadores del Estado</b>: riesgo de recortes salariales o de servicios.\n<b>Empresario privado</b>: gana mayor rentabilidad por el ajuste de precios.",
    letraChica: "Permite ajustes de precios sin control previo, favoreciendo al contratista y limitando la fiscalización del gasto público."
  },
  {
    fecha: "2026-10-07",
    jurisdiccion: "pba",
    titulo: "Resolución 150/2023",
    criollo: "Se amplía la línea federal de inversión para PyMEs con tasa variable y se compensa la tasa de los préstamos del programa provincial, destinando $7.015.630 al Banco de la Provincia. Beneficia a las PyMEs y a sus trabajadores, pero carga al erario público y favorece al sector financiero.",
    afecta: "- <b>Financiamiento PyME</b>: ampliación de crédito con tasa variable.\n- <b>Presupuesto provincial</b>: gasto de 7,0 M$ en compensación de tasas.\n- <b>Empleo</b>: potencial generación de puestos en sectores industriales.",
    letraChica: "Se destina 7.015.630,31 pesos del presupuesto general a compensar tasas, sin indicar la fuente de financiamiento, aumentando la carga fiscal."
  },
  {
    fecha: "2026-10-07",
    jurisdiccion: "pba",
    titulo: "Resolución 84/2025",
    criollo: "Se mantiene el programa de créditos con bonificación de tasa para pymes industriales, con el Estado pagando la diferencia de intereses. Beneficia a las empresas y al banco provincial, pero usa 59,6 M de fondos públicos, sin garantía directa de generación de empleo.",
    afecta: "- <b>Financiamiento a pymes</b> crédito bonificado que facilita inversión y empleo.\n- <b>Subsidio de intereses</b> el Estado cubre la tasa, carga al presupuesto provincial.\n- <b>Presupuesto provincial</b> desembolso de $59.6 M que podría destinarse a servicios públicos.",
    letraChica: "El Estado asume $59.632.031,01 para compensar la tasa del banco, una carga fiscal oculta para el contribuyente."
  },
  {
    fecha: "2026-10-07",
    jurisdiccion: "pba",
    titulo: "Resolución 377/2025",
    criollo: "El Estado paga la bonificación de intereses de hasta $361 M a los créditos que el Banco de la Provincia otorga a microemprendedores. Busca impulsar la producción y generar puestos de laburo, pero el beneficio recae en los dueños de las MiPyMEs, no garantiza empleo ni salarios dignos y consume fondos públicos que podrían destinarse a políticas de pleno empleo.",
    afecta: "- <b>Financiamiento a microempresas</b>: subsidio de intereses que reduce costos de crédito.\n- <b>Presupuesto público</b>: destina $361 M del erario, disminuye recursos para otras políticas.\n- <b>Empleo</b>: potencial creación de puestos, sin garantía de salarios dignos.",
    letraChica: "El subsidio cubre solo la tasa de interés y no incluye mecanismos de seguimiento que demuestren la generación real de empleo ni la distribución equitativa del crédito."
  },
  {
    fecha: "2026-10-07",
    jurisdiccion: "caba",
    titulo: "Resolución 661/SSASS/26",
    criollo: "Se aprueba un nuevo gasto para contratar a una empresa privada que administre, opere y mantenga el Hospital Municipal de Quemados, incluida la limpieza de residuos y obras menores. El presupuesto extra recorta plazas estatales, precariza el trabajo de los empleados hospitalarios y beneficia a la compañía adjudicataria, sin garantía de mejora en la atención.",
    afecta: "- <b>Empleo hospitalario</b>: reducción de plazas estatales y precarización del personal de limpieza y mantenimiento.\n- <b>Presupuesto público</b>: aumento del gasto sin especificar monto, desvío de fondos del Estado.\n- <b>Calidad de atención</b>: riesgo de deterioro al delegar servicios críticos a empresa privada.",
    letraChica: "No se indica el monto del adicional ni los criterios de adjudicación, permitiendo una asignación discrecional a la empresa contratista."
  },
  {
    fecha: "2026-10-07",
    jurisdiccion: "caba",
    titulo: "Resolución 696/SAGYP/26",
    criollo: "La Resolución 696/SAGYP/26 fija una nueva Adecuación Provisoria de Precios para la licitación 2‑0032‑LPU25, rebajando los valores de referencia. Con ello se favorece a los grandes proveedores que pueden absorber los precios bajos, mientras se recorta el presupuesto de obras o servicios públicos, lo que puede traducirse en menos puestos de trabajo y menor calidad para la comunidad.",
    afecta: "- <b>Presupuesto público</b>: rebaja el monto de la licitación, recortando gasto estatal.\n- <b>Trabajadores del sector</b>: menor inversión puede generar menos empleos y salarios más bajos.\n- <b>Empresas contratistas</b>: favorece a grandes grupos que pueden competir con precios bajos.",
    letraChica: "En la letra chica se permite la revisión unilateral de precios por el Estado sin consulta a los oferentes, limitando la certeza contractual."
  },
];
