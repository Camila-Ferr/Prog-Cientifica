using JSON


function readJSON()
    file = open("dem_input.json")
    data = JSON.parse(file)
    ne = size(data["coordenadas"])[1]
    x0 = Array{Float64}(undef,ne,1)
    y0 = Array{Float64}(undef,ne,1)
    conect = Matrix{Int64}(undef,ne,5)
    force = Matrix{Float64}(undef,ne,2)
    resistence = Matrix{Int64}(undef,ne,2)

    for i=1:ne
        x0[i] = convert(Float64,data["coordenadas"][i][1])
        y0[i] = convert(Float64,data["coordenadas"][i][2])
        for j=1:5
            conect[i,j] = convert(Int64,data["connective"][i][j])
        end
        for j=1:2
            force[i,j] = convert(Float64,data["force"][i][j])
            resistence[i,j] = convert(Int64,data["resistence"][i][j])
        end
    end
    mass = convert(Float64,data["mass"])
    kspr = convert(Float64,data["density"])

    return ne,x0,y0,conect,force,resistence,mass,kspr
end


function outputRes(_res)
    dict = Dict()
    push!(dict,"resultado"=>_res)
    open("dem_output.json","w") do f
        JSON.print(f,dict)
    end
end

function main()
    println(".DEM")
    # read input file
    N = 600
    h = 0.00004
    ne, x0, y0, conect, F, restrs, mass, kspr = readJSON()
    ndofs = 2*ne
    raio = 1

    F = reshape(transpose(F),(ndofs,1))
    restrs = reshape(transpose(restrs),(ndofs,1))
        
    @show ne

    u = zeros(Float64,ndofs,1)
    v = zeros(Float64,ndofs,1)
    a = zeros(Float64,ndofs,1)
    res = zeros(Float64,N)

    fi = zeros(Float64,ndofs,1)
    a .= (F .- fi)./mass    
    for i = 1:N
        v .+= a .* (0.5*h)
        u .+= v .* h
        fi .= 0.0
        for j = 1:ne
            if (restrs[2*j-1] == 1)
                u[2*j-1] = 0.0
            end
            if (restrs[2*j] == 1)
                u[2*j] = 0.0
            end
            xj = x0[j] + u[2*j-1]
            yj = y0[j] + u[2*j]
            for index = 1:conect[j,1]
                k = conect[j,index+1]
                xk = x0[k] + u[2*k-1]
                yk = y0[k] + u[2*k]
                dX = xj-xk
                dY = yj-yk
                di = sqrt(dX*dX+dY*dY)
                d2 = (di - 2*raio)
                dx = d2*dX/di
                dy = d2*dY/di
                fi[2*j-1] += kspr*dx
                fi[2*j] += kspr*dy
            end
        end
        a .= (F .- fi)./mass
        v .+= a .* (0.5*h)
        res[i] = u[33]
    end
    outputRes(res)
    x = 1:N
    # plot(x,res)
end

main()
