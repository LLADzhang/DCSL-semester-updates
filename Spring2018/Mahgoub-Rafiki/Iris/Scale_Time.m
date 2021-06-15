function [ scale_t ] = Scale_Time( t, val )
    
    
wl_length = length(t);
%scale_t = zeros(1,wl_length);
scale_t=[];

if(val > 0)

        step = wl_length / val;
        sub_scale = zeros(step,1);
        for i=1:1:step
            sub_scale(i,1) = t(val*i,1);
        end
        for i=1:val
            scale_t = [scale_t; sub_scale];
        end
        
        
else
        count = 1;
        step = 0 ;
        val = val * -1;
        for i =1:wl_length
            scale_t(i,1) = t(count,1);
            if(step >= val)
                count = count + 1;
                step =0;
            end
            step = step+1;
        end
end



end