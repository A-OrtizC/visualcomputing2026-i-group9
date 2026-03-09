Shader "Custom/MyCustomShader"
{
    Properties
    {
        [MainColor] _BaseColor("Base Color", Color) = (1, 1, 1, 1)
        [MainTexture] _BaseMap("Base Map", 2D) = "white" {}
        _WaveSpeed("Wave Speed", Float) = 2.0 // Control para la velocidad
        _WaveFreq("Wave Frequency", Float) = 5.0 // Control para la frecuencia
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }

        Pass
        {
            HLSLPROGRAM

            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL; // SE AÑADIÓ: Entrada de normales
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float3 normalWS : TEXCOORD1; // SE AÑADIÓ: Salida de normales al mundo
                float2 uv : TEXCOORD0;
            };

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                float4 _BaseMap_ST;
                float _WaveSpeed; // SE AÑADIÓ
                float _WaveFreq;  // SE AÑADIÓ
            CBUFFER_END

            Varyings vert(Attributes IN)
            {
                Varyings OUT;
                
                // --- SECCIÓN DE DEFORMACIÓN (Vertex Shader) ---
                float3 pos = IN.positionOS.xyz;
                // Deformación senoidal basada en el tiempo y posición X
                pos.y += sin(pos.x * _WaveFreq + _Time.y * _WaveSpeed) * 0.2;
                
                // Transformación a Clip Space (obligatorio)
                OUT.positionHCS = TransformObjectToHClip(pos);
                
                // Transformación de normales al espacio de mundo
                OUT.normalWS = TransformObjectToWorldNormal(IN.normalOS);
                
                OUT.uv = TRANSFORM_TEX(IN.uv, _BaseMap);
                return OUT;
            }

            half4 frag(Varyings IN) : SV_Target
            {
                // --- SECCIÓN DE ILUMINACIÓN (Fragment Shader) ---
                // 1. Obtener textura base
                half4 texColor = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, IN.uv) * _BaseColor;
                
                // 2. Cálculo de iluminación Lambert básica
                float3 lightDir = normalize(float3(0.5, 1.0, 0.5)); // Dirección de luz manual
                float3 normal = normalize(IN.normalWS);
                float diffuse = max(0.0, dot(normal, lightDir)); // Producto punto
                
                // 3. Resultado: Color x Iluminación
                return half4(texColor.rgb * diffuse, texColor.a);
            }
            ENDHLSL
        }
    }
}