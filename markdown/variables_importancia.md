### 🔹 Variables ordenadas por importancia

#### 1. 🌧️ Precipitación
- **precipitacion_pluviometrica**  
👉 Es la más importante, porque la lluvia genera y mantiene los criaderos de *Aedes* (acumulación de agua en recipientes). Una mayor frecuencia o intensidad de lluvias aumenta directamente la población de mosquitos.  

---

#### 2. 🌡️ Temperatura
- **temperatura_abrigo_150cm_minima**  
- **temperatura_abrigo_150cm_maxima**  
- **temperatura_abrigo_150cm (media)**  
👉 La temperatura es crítica: regula la supervivencia de larvas, la actividad de mosquitos adultos y la velocidad de replicación del virus dentro del vector (periodo de incubación extrínseca). Las mínimas marcan la supervivencia en condiciones frías y las máximas limitan la viabilidad por exceso de calor.  

---

#### 3. 💧 Humedad
- **humedad_media_8_14_20**  
- **rocio_medio**  
- **tesion_vapor_media**  
👉 La humedad relativa prolonga la vida del mosquito adulto y mantiene viables los huevos. El rocío y la tensión de vapor son medidas complementarias que reflejan la humedad ambiental real.  

---

#### 4. 🌞 Radiación y sol
- **radiacion_global**  
- **heliofania_efectiva**  
- **heliofania_relativa**  
👉 Regulan la evaporación del agua en criaderos y la temperatura ambiental. Días más soleados y secos reducen la permanencia de agua estancada, mientras que baja radiación favorece la persistencia de criaderos.  

---

#### 5. 🌬️ Viento
- **velocidad_viento_200cm_media**  
- **velocidad_viento_1000cm_media**  
👉 El viento influye en la dispersión de mosquitos adultos. Aunque no es determinante como lluvia o temperatura, puede modular la propagación espacial en áreas urbanas.  

---

#### 6. 📅 Variables de control
- **fecha**  
👉 Fundamental para el análisis temporal y estacionalidad (detección de picos de brotes, estacionalidad anual).  

- **id_estacion**  
👉 No es predictiva directamente, pero sirve como identificador geográfico para distinguir entre estaciones o zonas de medición.  

---

#### 7. ❌ Menor relevancia
- **horas_frio**  
👉 Tiene muy poca relación con la dinámica del dengue (más asociada a agricultura y climas fríos). Se puede descartar salvo que quieras explorar estacionalidad extrema.  

- **direccion_viento_200cm / direccion_viento_1000cm**  
👉 Generalmente poco útiles para modelos epidemiológicos, salvo en estudios muy específicos de dispersión espacial.  


```python
variables_dengue_ranked = [
    # Variables de control
    "fecha",
    "id_estacion",
    
    # Muy alta importancia
    "precipitacion_pluviometrica",
    "temperatura_abrigo_150cm_minima",
    "temperatura_abrigo_150cm_maxima",
    "temperatura_abrigo_150cm",
    
    # Alta importancia
    "humedad_media_8_14_20",
    "rocio_medio",
    "tesion_vapor_media",
    
    # Importancia media
    "radiacion_global",
    "heliofania_efectiva",
    "heliofania_relativa",
    "velocidad_viento_200cm_media",
    "velocidad_viento_1000cm_media"
]


```