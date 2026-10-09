// Base de datos viva y acumulativa de IPD
const baseDatosIPD = [
  {
    fecha: "2026-10-09",
    jurisdiccion: "nacion",
    titulo: "Resolución 69/2026",
    criollo: "El Estado abre la puerta a la privatización de servicios aeroportuarios, reduciendo plazas estatales y transfiriendo la gestión a grupos empresariales. ¿A quién le sirve? A los grandes inversores, no al trabajador. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Empleos estatales:</b> recorta plazas en aeropuertos, precariza al personal.\n- <b>Tarifas y pasajes:</b> suben costos que paga el pasajero y el trabajador.\n- <b>Beneficio empresarial:</b> favorece a constructoras y fondos extranjeros, sin garantía de empleo.",
    letraChica: "Permite prórroga automática de concesiones aeroportuarias por 30 años sin revisión de tarifas, transfiriendo rentas al sector privado."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "nacion",
    titulo: "Resolución 408/2026",
    criollo: "El Estado crea un régimen simplificado para pymes que les permite contratar a los trabajadores con contratos precarios y pagar menos impuestos. ¿A quién le sirve? A los dueños de empresas que buscan reducir costos, no a los laburantes que pierden estabilidad. Al final, la cuenta la paga el pueblo.",
    afecta: "- <b>Empleo precario:</b> se permite contratar con contratos temporales y sin cobertura, desprotegiendo al trabajador.\n- <b>Menor recaudación:</b> los descuentos fiscales reducen el presupuesto estatal, que paga con los impuestos de los laburantes.",
    letraChica: "Incluye una prórroga de 5 años de la exención tributaria sin control de resultados, beneficiando a grandes grupos empresariales que ya operan en el sector."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "nacion",
    titulo: "Resolución 191/2026",
    criollo: "El Estado simplifica los permisos de exportación agropecuaria, quitando controles sanitarios y reduciendo la fiscalización en puertos. ¿A quién le sirve? A los grandes exportadores que ahorran costos. ¿Quién paga? Los laburantes del campo y del puerto que pierden empleo y seguridad. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Empleo en puertos:</b> se recortan puestos de inspección, afecta a guardias y operarios\n- <b>Seguridad alimentaria:</b> se promete mayor exportación, pero no hay garantía de calidad ni de precios para el productor\n- <b>Pequeños productores:</b> pierden acceso a mercados por competencia desleal",
    letraChica: "En el artículo final se otorgan exenciones impositivas a empresas exportadoras con capital extranjero, sin compensar al fisco ni al trabajador."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "pba",
    titulo: "Resolución 127/2026",
    criollo: "El Estado destina $625,781,536 a comprar molinos, elevadores y demás equipos para el programa “Mi Provincia Recicla”. La licitación la ganan firmas privadas; el gasto lo paga el contribuyente y la promesa de empleo para los recuperadores urbanos no está garantizada.",
    afecta: "- <b>Presupuesto público:</b> se gasta $625 M sin garantía de empleo.\n- <b>Recuperadores urbanos:</b> se promete inclusión, pero depende de contratos privados.\n- <b>Empresas proveedoras:</b> obtienen contratos millonarios con fondos del Estado.",
    letraChica: "El pliego permite adjudicar sin exigir participación de cooperativas de recuperadores, favoreciendo a grandes proveedores y dejando fuera al trabajo popular."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "pba",
    titulo: "Decreto 90/2022",
    criollo: "El Estado declara el turismo prioridad y lanza un plan de fomento con subsidios y facilidades impositivas a empresas turísticas. ¿A quién le sirve? A los grandes operadores y fondos de inversión, no a los laburantes. Se promete más puestos, pero sin garantía de empleo estable ni salarios dignos. Al final, la cuenta la paga el pueblo.",
    afecta: "- <b>Empleos precarios:</b> se incentiva contratación temporal sin derechos, afecta al trabajador.\n- <b>Subsidios a empresas:</b> el ahorro público se destina a grandes grupos, no a pequeños comercios.\n- <b>Impuestos reducidos:</b> se pierde recaudación que podría financiar servicios al barrio.",
    letraChica: "La norma permite exonerar IVA e impuesto a los ingresos a cualquier empresa turística autorizada, sin límite de monto, desviando recursos del Estado a capitales externos y dejando sin fondos a salud y vivienda."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "pba",
    titulo: "Decreto 312/25",
    criollo: "El Estado destina hasta 20 millones por proyecto al Sudoeste, pero solo cubre el 50% del costo y no permite gastos corrientes. ¿A quién le sirve? A los agroempresarios con capacidad de presentar proyectos, mientras el laburante sigue sin empleo estable. La cuenta la paga el presupuesto provincial.",
    afecta: "- <b>Empleo local:</b> se promete crear puestos, pero el aporte no cubre gastos corrientes, limitando contratación.\n- <b>Presupuesto público:</b> el gasto proviene de fondos provinciales, lo paga el contribuyente y el trabajador.\n- <b>Productores:</b> beneficia a agroempresarios con proyectos, deja fuera a pequeños laburantes.",
    letraChica: "El financiamiento no reintegrable del 50% del costo, con tope de 20 millones, excluye gastos operativos y favorece a quienes ya disponen de capital, desviando recursos del erario sin garantía de generación real de empleo."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "caba",
    titulo: "Resolución 557/2026",
    criollo: "El Estado aprueba la primera a la trigésima cuarta redeterminación de precios de la licitación pública 648‑SIGAF/18, ajustando los valores a los que reclaman los proveedores adjudicatarios. ¿A quién le sirve? A los grandes contratistas que cobran más. ¿Quién paga? El contribuyente, que verá recortado el presupuesto de salud, educación y obras. No hay garantía de que esos ajustes generen empleo; al revés, pueden provocar nuevos recortes de personal. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Precio inflado</b>: eleva gasto público y recorta fondos sociales.\n- <b>Beneficio a empresas</b>: favorece a los contratistas, sin garantía de empleo.\n- <b>Riesgo de recortes</b>: obliga a bajar salarios o despedir al personal estatal.",
    letraChica: "En la letra chica se permite la renegociación unilateral de precios y la prórroga automática del contrato, sin control de la Auditoría, lo que favorece a los proveedores y deja al Estado sin defensa."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "caba",
    titulo: "Resolución 556/MEPHUGC/26",
    criollo: "El Estado reduce el precio definitivo de la licitación pública 651‑SIGAF/16, bajando el presupuesto de la obra. ¿A quién le sirve? A los proveedores que buscan mayor margen y al capital que ahorra, mientras se recortan fondos para la mano de obra. No hay garantía de empleo ni de salarios. Al final, la cuenta la paga el trabajador.",
    afecta: "- <b>Presupuesto de obra reducido:</b> menos fondos para pagar salarios y materiales.\n- <b>Empleos en riesgo:</b> se prometen ahorros, pero se recortan puestos de trabajo.\n- <b>Beneficio a proveedores:</b> se favorece a empresas que aceptan precios bajos, no al trabajador.",
    letraChica: "La resolución autoriza revisiones de precios y prórrogas sin control, lo que beneficia a los consorcios adjudicatarios y deja al Estado sin recursos para pagar a los laburantes."
  },
  {
    fecha: "2026-10-09",
    jurisdiccion: "caba",
    titulo: "Resolución 232/SSAH/26",
    criollo: "Se autoriza que la Asociación Servicio para la Equidad Social reajuste los aranceles de la atención a niños y adolescentes con salud mental y discapacidad. ¿A quién le sirve? A la entidad y al Estado que recorta gasto. ¿Quién paga? Las familias y, en última instancia, los contribuyentes. Al final, la cuenta la pagamos entre todos.",
    afecta: "- <b>Aranceles más altos:</b> familias deben pagar más por servicios esenciales\n- <b>Recorte de gasto público:</b> el Estado ahorra, pero la atención depende de la entidad privada\n- <b>Precarización laboral:</b> la asociación puede recortar personal, afectando empleo y calidad",
    letraChica: "La resolución permite ajustes anuales de tarifas sin límite y sin control de precios, beneficiando a la asociación y a proveedores privados mientras la carga recae en las familias y el erario."
  },
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
