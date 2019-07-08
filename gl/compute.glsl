#version 460

layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

layout(binding=0) buffer bind_0
{
    vec4 data[];
};

uniform float u_width;
uniform float u_height;
uniform float u_depth;
uniform float u_time;


float random(float n) { return fract(sin(n) * 43758.5453123); }
vec3 permute(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
float simplex(vec2 uv)
{
    const vec4 C = vec4(
         0.211324865405187, 0.366025403784439,
        -0.577350269189626, 0.024390243902439
    );

    vec2 i = floor(uv + dot(uv, C .yy));
    vec2 x0 = uv - i + dot(i, C.xx);
    vec2 i1 = x0.x > x0.y ? vec2(1.0, 0.0) : vec2(0.0, 1.0);

    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod(i, 289.0);
    vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));

    vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
    m = m * m;
    m = m * m;

    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
    vec3 g;
    g.x = a0.x * x0.x + h.x * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}


void main()
{
    uvec3 xyz = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;
    uint i = uint(xyz.x + xyz.y * u_width + xyz.z * u_width * u_height);

    vec3 uvw = xyz.xyz / vec3(u_width, u_height, u_depth);

    vec2 uv = uvw.xy;
    uv = uv * 12.5;
    // uv = fract(uv);

    float simplex_x = simplex(uv);
    uvw = vec3(simplex_x);

    vec3 RGB = vec3(uvw);

    data[i] = vec4(RGB, 1.0);
}
