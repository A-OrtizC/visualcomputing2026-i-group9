Shader "Custom/SimplePBR"
{
    Properties
    {
        _MainTex ("Albedo", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
        _Metallic ("Metallic", Range(0,1)) = 0
        _Roughness ("Roughness", Range(0,1)) = 0.5
        _SpecularIntensity ("Specular Intensity", Range(0,2)) = 1
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        LOD 100
        
        Pass
        {
            Name "SimplePBRPass"
            Tags { "LightMode"="UniversalForward" }
            
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            
            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };
            
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
                float3 viewDirWS : TEXCOORD3;
            };
            
            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                float4 _Color;
                float _Metallic;
                float _Roughness;
                float _SpecularIntensity;
            CBUFFER_END
            
            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _MainTex);
                output.viewDirWS = normalize(_WorldSpaceCameraPos - output.positionWS);
                return output;
            }
            
            half4 frag(Varyings input) : SV_Target
            {
                half4 albedo = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv) * _Color;
                
                Light mainLight = GetMainLight();
                float3 lightDir = normalize(mainLight.direction);
                float3 normalWS = normalize(input.normalWS);
                float3 viewDirWS = normalize(input.viewDirWS);
                
                // Calcular NdotL para difuso
                float NdotL = max(0, dot(normalWS, lightDir));
                
                // Ajuste de reflectividad según metalness
                // Metalness 0 (dieléctrico): reflectividad baja
                // Metalness 1 (metal): reflectividad alta
                float f0 = lerp(0.04, 0.9, _Metallic); // Fresnel en incidencia 0
                
                // Roughness afecta la distribución especular
                float roughness2 = _Roughness * _Roughness;
                
                // Blinn-Phong con ajustes PBR
                float3 halfVec = normalize(lightDir + viewDirWS);
                float NdotH = max(0, dot(normalWS, halfVec));
                
                // Distribución especular simplificada (Beckmann-like)
                float specularDistribution = pow(NdotH, 1.0 / roughness2);
                
                // Fresnel Schlick approximation
                float VdotH = max(0, dot(viewDirWS, halfVec));
                float3 fresnel = f0 + (1.0 - f0) * pow(1.0 - VdotH, 5.0);
                
                // Componente especular con metalness
                half3 specular = fresnel * _SpecularIntensity * mainLight.color * specularDistribution;
                
                // Componente difuso: los metales no tienen difuso
                half3 diffuse;
                if (_Metallic > 0.99)
                {
                    diffuse = half3(0, 0, 0); // Metal puro: sin difuso
                }
                else
                {
                    float kd = (1.0 - _Metallic) * (1.0 - f0);
                    diffuse = albedo.rgb * kd * mainLight.color * NdotL;
                }
                
                // Ambient simplificado
                half3 ambient = albedo.rgb * 0.1 * (1.0 - _Metallic * 0.5);
                
                half3 finalColor = ambient + diffuse + specular;
                
                return half4(finalColor, albedo.a);
            }
            ENDHLSL
        }
    }
}