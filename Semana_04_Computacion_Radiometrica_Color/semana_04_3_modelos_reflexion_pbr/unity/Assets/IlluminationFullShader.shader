Shader "Custom/FullIllumination"
{
    Properties
    {
        _MainTex ("Albedo", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
        _SpecularColor ("Specular Color", Color) = (1,1,1,1)
        _Shininess ("Shininess", Range(1, 256)) = 32
        _AmbientIntensity ("Ambient Intensity", Range(0,1)) = 0.1
        _DiffuseIntensity ("Diffuse Intensity", Range(0,2)) = 1
        _SpecularIntensity ("Specular Intensity", Range(0,2)) = 1
        [Toggle] _IsMetal ("Metallic Look", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        LOD 100
        
        Pass
        {
            Name "FullIlluminationPass"
            Tags { "LightMode"="UniversalForward" }
            
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma shader_feature _ISMETAL_ON
            
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
                float4 _SpecularColor;
                float _Shininess;
                float _AmbientIntensity;
                float _DiffuseIntensity;
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
                
                // Ambient: I_ambient = k_a * albedo
                half3 ambient = _AmbientIntensity * albedo.rgb;
                
                // Diffuse: I_diffuse = I_light * k_d * max(N·L, 0)
                float NdotL = max(0, dot(normalWS, lightDir));
                half3 diffuse = mainLight.color * albedo.rgb * NdotL * _DiffuseIntensity;
                
                // Specular usando Blinn-Phong
                float3 halfVec = normalize(lightDir + viewDirWS);
                float NdotH = max(0, dot(normalWS, halfVec));
                half3 specular = _SpecularColor.rgb * _SpecularIntensity * mainLight.color * pow(NdotH, _Shininess);
                
                // Ajuste para material metálico vs plástico
                #ifdef _ISMETAL_ON
                    // Metálico: especular más intenso, menos difuso
                    specular *= 1.5;
                    diffuse *= 0.7;
                #else
                    // Plástico: especular más sutil
                    specular *= 0.8;
                #endif
                
                // I_total = I_ambient + I_diffuse + I_specular
                half3 finalColor = ambient + diffuse + specular;
                
                return half4(finalColor, albedo.a);
            }
            ENDHLSL
        }
    }
}