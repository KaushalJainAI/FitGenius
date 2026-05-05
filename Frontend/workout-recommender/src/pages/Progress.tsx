import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Target, TrendingUp, Zap } from 'lucide-react';

const data = [
  { name: 'Week 1', weight: 70, setsCompleted: 24, consistency: 80 },
  { name: 'Week 2', weight: 69.5, setsCompleted: 28, consistency: 85 },
  { name: 'Week 3', weight: 69.2, setsCompleted: 32, consistency: 90 },
  { name: 'Week 4', weight: 68.8, setsCompleted: 34, consistency: 95 },
  { name: 'Week 5', weight: 68.4, setsCompleted: 36, consistency: 100 },
  { name: 'Week 6', weight: 68.0, setsCompleted: 40, consistency: 100 },
];

export default function Progress() {
  return (
    <div className="space-y-6 animate-content-reveal">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8">
         <div>
            <h2 className="text-2xl font-bold">Progress Analytics</h2>
            <p className="text-muted-foreground mt-1">Track your consistency and metric improvements.</p>
         </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8 stagger-children">
         <div className="bg-card border border-border p-6 rounded-2xl shadow-sm hover-lift">
            <div className="flex items-center gap-4">
               <div className="w-12 h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center">
                  <TrendingUp />
               </div>
               <div>
                  <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Weight Log</p>
                  <h3 className="text-2xl font-bold">68.0 <span className="text-sm font-normal text-muted-foreground">kg</span></h3>
               </div>
            </div>
            <div className="mt-4 text-sm font-medium text-green-500">
               ↓ 2.0 kg from start
            </div>
         </div>

         <div className="bg-card border border-border p-6 rounded-2xl shadow-sm hover-lift">
            <div className="flex items-center gap-4">
               <div className="w-12 h-12 bg-secondary/10 text-secondary rounded-xl flex items-center justify-center">
                  <Target />
               </div>
               <div>
                  <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Sets Completed</p>
                  <h3 className="text-2xl font-bold">194</h3>
               </div>
            </div>
            <div className="mt-4 text-sm font-medium text-secondary">
               ↑ 16.6% from last week
            </div>
         </div>

         <div className="bg-card border border-border p-6 rounded-2xl shadow-sm hover-lift relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-accent/20 rounded-full blur-2xl -mr-8 -mt-8 transition-smooth group-hover:bg-accent/30"></div>
            <div className="flex items-center gap-4 relative z-10">
               <div className="w-12 h-12 bg-accent/10 text-accent rounded-xl flex items-center justify-center">
                  <Zap />
               </div>
               <div>
                  <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Consistency</p>
                  <h3 className="text-2xl font-bold">100%</h3>
               </div>
            </div>
            <div className="mt-4 text-sm font-medium text-accent relative z-10">
               Flawless week!
            </div>
         </div>
      </div>

      <div className="bg-card border border-border rounded-2xl shadow-card overflow-hidden">
         <div className="border-b border-border p-6 bg-muted/20">
            <h3 className="font-semibold text-lg">Weight Loss Trajectory Vs Sets Volume</h3>
         </div>
         <div className="p-6 h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
               <AreaChart
                  width={500}
                  height={400}
                  data={data}
                  margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
               >
                  <defs>
                     <linearGradient id="colorWeight" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                     </linearGradient>
                     <linearGradient id="colorSets" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--secondary))" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(var(--secondary))" stopOpacity={0}/>
                     </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" tick={{fill: 'hsl(var(--muted-foreground))'}} tickLine={false} axisLine={false} dy={10} />
                  <YAxis yAxisId="left" stroke="hsl(var(--muted-foreground))" tick={{fill: 'hsl(var(--muted-foreground))'}} tickLine={false} axisLine={false} domain={['dataMin - 1', 'dataMax + 1']} />
                  <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--muted-foreground))" tick={{fill: 'hsl(var(--muted-foreground))'}} tickLine={false} axisLine={false} />
                  <Tooltip 
                     contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '12px', color: 'hsl(var(--foreground))' }}
                     itemStyle={{ fontWeight: 500 }}
                  />
                  <Area yAxisId="left" type="monotone" dataKey="weight" stroke="hsl(var(--primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorWeight)" activeDot={{ r: 8, fill: 'hsl(var(--primary))' }} />
                  <Area yAxisId="right" type="monotone" dataKey="setsCompleted" stroke="hsl(var(--secondary))" strokeWidth={3} fillOpacity={1} fill="url(#colorSets)" />
               </AreaChart>
            </ResponsiveContainer>
         </div>
      </div>
    </div>
  );
}
