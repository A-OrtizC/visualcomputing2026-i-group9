Shader "Custom/DynamicFluid"
{
    Properties
    {
        _Color1 ("Color Principal", Color) = (1,0,0,1)
        _Color2 ("Color Secundario", Color) = (0,0,1,1)
        _Speed ("Velocidad de Fluido", Float) = 2.0
        _Amount ("Fuerza de Distorsión", Float) = 0.2
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 worldPos : TEXCOORD0;
            };

            float4 _Color1;
            float4 _Color2;
            float _Speed;
            float _Amount;

            v2f vert (appdata v)
            {
                v2f o;
                
                // 1. Calcular el tiempo
                float time = _Time.y * _Speed;
                
                // 2. Desplazar el vértice usando la normal y el seno de la posición en Y
                float displacement = sin(v.vertex.y * 5.0 + time) * _Amount;
                v.vertex.xyz += v.normal * displacement;
                
                // 3. Transformar la posición a la pantalla
                o.pos = UnityObjectToClipPos(v.vertex);
                
                // 4. Guardar la posición del mundo para el color
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                // Mezclar colores basado en la altura y el tiempo
                float mixValue = (sin(i.worldPos.y * 3.0 + _Time.y * _Speed) + 1.0) * 0.5;
                fixed3 finalColor = lerp(_Color1.rgb, _Color2.rgb, mixValue);
                
                return fixed4(finalColor, 1.0);
            }
            ENDCG
        }
    }
}