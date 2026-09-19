const real=(id,name,c)=>Object.freeze({id,name,evidence:'conventional',model:'aerodynamic-6dof',...c});
const experimental=(id,name,c)=>Object.freeze({id,name,evidence:'experimental-simulation',model:'adapter',...c});
export const VEHICLES=Object.freeze({
 f16:real('f16','F-16',{massKg:12000,inertia:[12875,75674,85552],wing:{area:27.87,span:9.96,chord:3.45},aero:{CL0:.18,CLa:4.6,CD0:.022,k:.085,Cm0:.02,Cma:-.62,Clp:-.42,Cnr:-.28,ClDa:.13,CmDe:-1.05,CnDr:.17,CyBeta:-.72,CyDr:.21},propulsion:'f100',limits:{alpha:.55,beta:.35,g:9}}),
 sr71:real('sr71','SR-71',{massKg:54000,inertia:[420000,3100000,3250000],wing:{area:167,span:16.94,chord:10.8},aero:{CL0:.12,CLa:2.65,CD0:.018,k:.065,Cm0:.01,Cma:-.38,Clp:-.22,Cnr:-.2,ClDa:.07,CmDe:-.52,CnDr:.09,CyBeta:-.45,CyDr:.12},propulsion:'j58',limits:{alpha:.32,beta:.2,g:3.5}}),
 x15:real('x15','X-15',{massKg:15400,inertia:[38000,210000,225000],wing:{area:18.6,span:6.8,chord:3.2},aero:{CL0:.05,CLa:2.2,CD0:.028,k:.12,Cm0:0,Cma:-.3,Clp:-.3,Cnr:-.16,ClDa:.08,CmDe:-.65,CnDr:.1,CyBeta:-.38,CyDr:.13},propulsion:'x15_rocket',limits:{alpha:.65,beta:.4,g:7}}),
 eidolon:experimental('eidolon','EIDOLON',{massKg:9000,inertia:[18000,26000,33000],propulsion:'eidolon_scalar'}),
 manta:experimental('manta','MANTA',{massKg:7200,inertia:[15000,23000,26000],propulsion:'manta_morph'}),
 skyrmion:experimental('skyrmion','SKYRMION',{massKg:8400,inertia:[17000,25000,30000],propulsion:'skyrmion_coherence'}),
 jacob:experimental('jacob','SYNTAX JACOB',{massKg:11000,inertia:[25000,36000,41000],propulsion:'syntax_jacob'}),
});
export const VEHICLE_ORDER=['f16','sr71','x15','eidolon','manta','skyrmion','jacob'];
export const vehicle=id=>VEHICLES[id]||VEHICLES.f16;
