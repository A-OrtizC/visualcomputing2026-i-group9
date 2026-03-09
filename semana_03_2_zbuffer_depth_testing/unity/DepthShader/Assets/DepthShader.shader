Shader "Custom/DepthShader"
{
    Properties {}
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float depth : TEXCOORD0;
            };

            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                // Calcula la profundidad en espacio de clip y la normaliza
                o.depth = UNITY_Z_0_FAR_FROM_CLIPSPACE(o.pos.z);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                // Visualiza la profundidad en escala de grises
                return fixed4(i.depth, i.depth, i.depth, 1.0);
            }
            ENDCG
        }
    }
}