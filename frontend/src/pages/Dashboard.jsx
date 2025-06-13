import { Box, Grid, Paper, Typography } from '@mui/material';
import {
  SmartToy as AgentIcon,
  AccountTree as WorkflowIcon,
  Email as EmailIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material';

function StatCard({ title, value, icon, color }) {
  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(255, 255, 255, 0.25)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.4)',
        borderRadius: '16px',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box
          sx={{
            background: `${color}15`,
            borderRadius: '12px',
            p: 1,
            mr: 2,
          }}
        >
          {icon}
        </Box>
        <Typography variant="h6" color="text.secondary">
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" sx={{ fontWeight: 600 }}>
        {value}
      </Typography>
    </Paper>
  );
}

function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 600 }}>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Aktywni Agenci"
            value="3"
            icon={<AgentIcon sx={{ color: '#007AFF' }} />}
            color="#007AFF"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Workflow"
            value="12"
            icon={<WorkflowIcon sx={{ color: '#30D158' }} />}
            color="#30D158"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Wiadomości"
            value="156"
            icon={<EmailIcon sx={{ color: '#FF9500' }} />}
            color="#FF9500"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Wydarzenia"
            value="8"
            icon={<CalendarIcon sx={{ color: '#AF52DE' }} />}
            color="#AF52DE"
          />
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Paper
          sx={{
            p: 3,
            background: 'rgba(255, 255, 255, 0.25)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.4)',
            borderRadius: '16px',
          }}
        >
          <Typography variant="h6" sx={{ mb: 2 }}>
            Ostatnie aktywności
          </Typography>
          <Typography color="text.secondary">
            Brak aktywności do wyświetlenia
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}

export default Dashboard; 