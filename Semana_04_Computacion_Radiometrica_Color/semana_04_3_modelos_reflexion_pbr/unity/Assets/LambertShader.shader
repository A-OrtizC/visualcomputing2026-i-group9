Shader "Custom/LambertDiffuse"
{
    Properties
    {
        _MainTex ("Albedo", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
        _DiffuseIntensity ("Diffuse Intensity", Range(0,2)) = 1
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        LOD 100
        
        Pass
        {
            Name "LambertPass"
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
            };
            
            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                float4 _Color;
                float _DiffuseIntensity;
            CBUFFER_END
            
            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _MainTex);
                return output;
            }
            
            half4 frag(Varyings input) : SV_Target
            {
                half4 albedo = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv) * _Color;
                
                // Obtener luz principal
                Light mainLight = GetMainLight();
                float3 lightDir = normalize(mainLight.direction);
                float3 normalWS = normalize(input.normalWS);
                
                // Ecuación Lambert: I_diffuse = I_light * k_d * max(N·L, 0)
                float NdotL = max(0, dot(normalWS, lightDir));
                half3 diffuse = mainLight.color * albedo.rgb * NdotL * _DiffuseIntensity;
                
                // Componente ambiental simple
                half3 ambient = half3(0.1, 0.1, 0.1) * albedo.rgb;
                
                half3 finalColor = ambient + diffuse;
                return half4(finalColor, albedo.a);
            }
            ENDHLSL
        }
    }
}