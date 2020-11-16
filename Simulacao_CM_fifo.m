%%%  This script models a Markov chain to capture timeline transient dynamics
%%%
%%%  Goals: understand the roles of 
%%%  
%%%% 0) population size 
%%%% 1) size of timeline 
%%%  2) position of posts in timeline on transient behavior of the system
%%%  3) the dependence between timeline and its neighbors (beyond NIMFA)
%%%
%%%
%%% note: we fill timeline from top
%%% 
%%%
%%%  
%%%
%%%
%%
%

% the total number of possible signatures per user is 4
%
nsigs=4; 
%%
% 00  no fake news
% 01  fake news at top
% 10  fake new at bottom
% 11  two fake news
%%

%% parameters to be configured

% setting initial state: 
% state 36 it is the state where all users have 1 
% fake news at top (local state 01), system state: 0 5 0 0 
inistate=36;

% state 1 it is the state where all users have no fake news 
% system state: 5 0 0 0 
%inistate=1


% lambda0=0.1;
% lambda1=0.2;

lambda0=0;
lambda1=0;


%%
% the total number of users is 5
%

nusers=5;
A=[0,0,0,0,0,1,1,1]
pA = perms(A);
uA = unique(pA,'rows')
nstates=factorial(nsigs+nusers-1)/(factorial(nusers)*factorial(nsigs-1));
B=zeros(factorial(nsigs+nusers-1)/(factorial(nusers)*factorial(nsigs-1)),nsigs);


%% in what follows, we have a messy way to generate the following 2 vectors:
% state2ind(xxx): converts a state into an index
% state{xxx}: converts an index into a state
% note: dont spend too much time trying to understand this part of the code 
% instead, try to find a more elegant way to write this
%
for i=1:size(uA,1)
    curele=1;
    j=1;
    while (j <= size(uA,2))
        count=0;
        while (j <= size(uA,2) && (uA(i,j)~=1))
            count=count+1;
            j=j+1;
            if (j==size(uA,2))
                break
            end
            
        end
        if (j==size(uA,2) && (uA(i,j)~=1))
            count=count+1;
        end
        B(i,curele)=count;
        curele=curele+1;
        j=j+1;
    end
end

state{nstates}=0;
keys=[];
values=0;
for i=1:nstates
    state{i}=B(i,:);
    disp(state{i});
    keys=[keys,state{i}(1)*1000+state{i}(2)*100+state{i}(3)*10+state{i}(4)];
end
state2ind=containers.Map(keys,1:nstates);

%%
%%% at this point, we have
%%% state2ind(0500) = 36 meaning that the index of state 0500 is 36
%%% state{36}=0 5 0 0 as state 36 corresponds to 5 users with signature 01
%%%

%%% double(strjoin(string(state{i})))


rate1=1; % rate of transmission of good or fake news, when transmitter has single good or fake news
rate2=2;  % rate of transmission of good or fake news, when transmitter has two good or two fake news

%clear Q;
Q = zeros(nstates,nstates)
% Gera matriz de transicao Q
for i=1:nstates
    curstate=state{i}; %5 0 0 0 
    curstateid=curstate(1)*1000+curstate(2)*100+curstate(3)*10+curstate(4); %5000
    if (curstate(1)>0)  % 00 === receive fake news ===> 01
        nextstate=curstate; %5 0 0 0
        nextstate(1)=curstate(1)-1; %4 0 0 0
        nextstate(2)=nextstate(2)+1; %4 1 0 0
        nextstateid=nextstate(1)*1000+nextstate(2)*100+nextstate(3)*10+nextstate(4); %4100
        Q(state2ind(curstateid),state2ind(nextstateid))=curstate(1)*((curstate(2)+curstate(3))*rate1 + curstate(4)*rate2 + lambda1);
        %Q(1,2) = 4 * (1+0) * 1 + 0*2 + lambda1(0) = 4*1*1+0+0 = 4
    end

    if (curstate(2)>0)  % 01 === receive fake news ===> 11
        nextstate=curstate;
        nextstate(2)=curstate(2)-1;
        nextstate(4)=nextstate(4)+1;
        nextstateid=nextstate(1)*1000+nextstate(2)*100+nextstate(3)*10+nextstate(4);
        Q(state2ind(curstateid),state2ind(nextstateid))=curstate(2)*((curstate(2)-1+curstate(3))*rate1 + curstate(4)*rate2 + lambda1);
    end

    if (curstate(2)>0)  % 01 === receive good news ===> 10
        nextstate=curstate;
        nextstate(2)=curstate(2)-1;
        nextstate(3)=nextstate(3)+1;
        nextstateid=nextstate(1)*1000+nextstate(2)*100+nextstate(3)*10+nextstate(4);
        Q(state2ind(curstateid),state2ind(nextstateid))=curstate(2)*((curstate(2)-1+curstate(3))*rate1 + curstate(1)*rate2 + lambda0);
    end

    
     if (curstate(3)>0)  % 10 === receive fake news ===> 01
        nextstate=curstate;
        nextstate(3)=curstate(3)-1;
        nextstate(2)=nextstate(2)+1;
        nextstateid=nextstate(1)*1000+nextstate(2)*100+nextstate(3)*10+nextstate(4);
        Q(state2ind(curstateid),state2ind(nextstateid))=curstate(3)*((curstate(2)+curstate(3)-1)*rate1 + curstate(4)*rate2 + lambda1);
    end

    
    if (curstate(3)>0)  % 10 === receive good news ====> 00
        nextstate=curstate;
        nextstate(3)=curstate(3)-1;
        nextstate(1)=nextstate(1)+1;
        nextstateid=nextstate(1)*1000+nextstate(2)*100+nextstate(3)*10+nextstate(4);
        Q(state2ind(curstateid),state2ind(nextstateid))=curstate(3)*((curstate(2)+curstate(3)-1)*rate1 + curstate(1)*rate2 + lambda0);
    end   
    
    if (curstate(4)>0)  % 11 === receive good news ====> 10
        nextstate=curstate;
        nextstate(4)=curstate(4)-1;
        nextstate(3)=nextstate(3)+1;
        nextstateid=nextstate(1)*1000+nextstate(2)*100+nextstate(3)*10+nextstate(4);
        Q(state2ind(curstateid),state2ind(nextstateid))=curstate(4)*((curstate(2)+curstate(3))*rate1 + curstate(1)*rate2 +  lambda0);
    end

    
end



%%
sumrows=sum(Q,2); %vetor coluna com a soma de cada linha


for i=1:nstates
    Q(i,i)=-sumrows(i); %subtrai da diagonal a soma da linha
end
inival=0.01;
inc=0.01;
maxt=6;


 
clear transient;
transient=zeros(max(size(inival:inc:maxt)),nstates);
tt=1;
for t=inival:inc:maxt
    trans=expm(Q*t);
    transient(tt,:)=trans(inistate,:);
    tt=tt+1;
end

% state 56 is last state, with index nstates, and equals: 0 0 0 5 
% at this state, all  5 users have timelines full with fake news
% figure
plot(inival:inc:maxt,transient(:,nstates), '--');
hold on
% state 1 is the first state, with index 1, and equals 5 0 0 0 
% at this state, all 5 users are free from fake news
plot(inival:inc:maxt,transient(:,1));

set(gca,'FontSize',24)
xlabel('time')
ylabel('state probability')
grid
legend('state (0 0 0 5): all fake','state (5 0 0 0): all non fake');
