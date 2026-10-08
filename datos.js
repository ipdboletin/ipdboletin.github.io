// Base de datos viva y acumulativa de IPD
const baseDatosIPD = [
  {
    fecha: "2026-10-08",
    jurisdiccion: "nacion",
    titulo: "Disposición 6489/2026",
    criollo: "El Estado crea un régimen de facilidades aduaneras para la importación de medicamentos y tecnología médica, reduciendo aranceles y simplificando trámites. ¿A quién le sirve? A los grandes laboratorios que ya dominan el mercado, no a los laburantes. Se promete mayor acceso, pero no hay garantía de precios más bajos. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Perdida de recaudación:</b> Se reducen aranceles y el Estado cobra menos, cargando la carga al presupuesto de salud.\n- <b>Precios más altos:</b> Al bajar controles, los laboratorios fijan precios sin garantía de rebaja para los pacientes.\n- <b>Empleos en riesgo:</b> La agencia delega funciones a privados, amenazando puestos de trabajo estatales.",
    letraChica: "La disposición autoriza a ARCA a gestionar la recaudación aduanera, transfiriendo ingresos al sector privado sin control parlamentario."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "nacion",
    titulo: "Resolución General 5911/2026",
    criollo: "El Estado amplía el plazo para presentar la declaración de Ganancias 2025. ¿A quién le sirve? A los que pueden postergar el pago y al fisco le faltan recursos para salud y empleo. El beneficio queda para quien difiere su aporte. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Retraso de ingresos públicos:</b> menos fondos para obras y salarios\n- <b>Ventaja a evasores:</b> se pospone el aporte y se fomenta la morosidad",
    letraChica: "La prórroga se publica sin señalar que reduce la recaudación prevista para financiar programas sociales, favoreciendo a grandes contribuyentes que pueden postergar su pago."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución 160/24",
    criollo: "El Estado provincial destina 9,9 millones de pesos a la cooperativa Abriendo Caminos, dentro del programa Cooperativas en Marcha. ¿A quién beneficia? A la entidad y a sus dirigentes, no al trabajador promedio. El dinero sale del presupuesto de los contribuyentes y se concentra en una sola empresa, sin garantía de crear empleo masivo. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Subsidio puntual:</b> 9,9 M$ van a una sola cooperativa, no a la mayoría de los trabajadores.\n- <b>Presupuesto público:</b> el gasto recae en los contribuyentes; no hay garantía de empleo sostenible.",
    letraChica: "La resolución se modifica por otras normas, permitiendo reasignar fondos sin control y favoreciendo cooperativas vinculadas al poder, sin rendición de resultados."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución RESO-2021-943-GDEBA-MIYSPGP",
    criollo: "El Estado paga más de 1.176 millones a la empresa contratista por redeterminación de precios y, a cambio, la empresa renuncia a cualquier reclamo por costos extra. ¿A quién beneficia este sobrecosto? A la compañía y a sus accionistas; el gasto recae en la provincia y, en última instancia, en los contribuyentes y los trabajadores que dependen de la inversión pública. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Sobreprecio:</b> la provincia paga 1.176 M extra, recorta recursos para obras y empleo.\n- <b>Renuncia a reclamos:</b> la empresa cede derechos, permite recortes salariales y menos garantías para sus empleados.\n- <b>Impacto fiscal:</b> el gasto se traslada al presupuesto, subiendo la carga tributaria para los laburantes.",
    letraChica: "La cláusula de renuncia a reclamos obliga a la empresa a absorber futuros sobrecostos, pero el Estado ya pagó 1.117 M y ahora reconoce 1.176 M, generando un sobrecosto de 58,9 M que recae en la hacienda provincial y, por ende, en los contribuyentes."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "pba",
    titulo: "Resolución 682/2026",
    criollo: "El Estado mantiene el Fondo Provincial de Compensaciones Tarifarias para que los concesionarios eléctricos con costos altos reciban subsidios y cobren lo mismo a todos los usuarios. ¿A quién le sirve? A los grandes concesionarios, mientras el trabajador sigue pagando la misma factura sin garantía de mejora. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Tarifas eléctricas</b>: se mantiene el precio para los laburantes sin garantía de baja, pese a subsidios a concesionarios.\n- <b>Presupuesto provincial</b>: se carga al erario, paga la gente con impuestos y tasas.\n- <b>Concesionarios</b>: reciben compensación sin control, se benefician de la medida.",
    letraChica: "Los faltantes del fondo se cubren con cargos extra a los usuarios, sin transparencia, trasladando el costo al contribuyente."
  },
  {
    fecha: "2026-10-08",
    jurisdiccion: "caba",
    titulo: "Resolución 557/MEPHUGC/26",
    criollo: "El Estado aprueba 34 redeterminaciones de precio en la licitación 648‑SIGAF/18, encareciendo obras y servicios públicos. ¿A quién le sirve? A los proveedores que ya tenían precios inflados, mientras el pueblo paga más impuestos o pierde calidad. Al final, la cuenta la paga el laburante.",
    afecta: "- <b>Gasto público inflado</b>: eleva el presupuesto sin mejora visible\n- <b>Beneficio a proveedores</b>: se garantiza precios altos, se promete inversión\n- <b>Carga al contribuyente</b>: se paga con impuestos, sin garantía de servicios",
    letraChica: "Incluye una cláusula de ajuste automático que permite subir precios hasta un 15 % sin nueva licitación, beneficiando a los contratistas y dejando al Estado sin control."
  },
];
