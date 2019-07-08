#version 460

layout(binding=0) buffer bind_0
{
    vec4 data[];
};

uniform float u_width;
uniform float u_height;
uniform float u_depth;

in vec2 vert_uv;
out vec4 out_fragcolor;

void main()
{
    const vec3 whd = vec3(u_width, u_height, u_depth);
    vec3 uvw = vec3(vert_uv, 0.0);
    vec3 xyz = uvw * whd;

    float idx = xyz.x + xyz.y * u_width + xyz.z * u_width * u_height;

    vec3 RGB = data[int(idx)].xyz;
    out_fragcolor = vec4(RGB, 1.0);
}
