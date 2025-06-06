import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  styled,
  useTheme,
  Fade,
  Card,
  CardContent,
  CardActionArea,
  alpha,
} from '@mui/material';
import {
  Tv as TvIcon,
  Headphones as AudioIcon,
  PhoneAndroid as MobileIcon,
  Computer as ComputersIcon,
  Kitchen as KitchenAppliancesIcon,
  Home as HomeAppliancesIcon,
  Thermostat as HvacIcon,
  LocalHospital as HealthcareIcon,
  Lightbulb as LightingIcon,
  SportsEsports as GamingIcon,
  CameraAlt as CameraIcon,
  Memory as ElectronicsIcon,
  Search as SearchIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const PageContainer = styled(Box)({
  width: '100%',
  position: 'relative',
  paddingTop: '24px'
});

const HeroBanner = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(5, 2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)'
    : 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
  textAlign: 'center',
  position: 'relative',
  overflow: 'hidden',
  marginBottom: theme.spacing(2),
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `radial-gradient(circle at 70% 30%, ${alpha(theme.palette.primary.light, 0.15)} 0%, transparent 70%)`,
  },
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `radial-gradient(circle at 30% 70%, ${alpha(theme.palette.secondary.light, 0.1)} 0%, transparent 70%)`,
  }
}));

const CategoryCard = styled(Card)(({ theme }) => ({
  height: '100%',
  backgroundColor: theme.palette.background.paper,
  transition: 'all 0.3s ease-in-out',
  border: `1px solid ${theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
  borderRadius: '20px',
  backdropFilter: 'blur(10px)',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)'
    : 'rgba(255, 255, 255, 0.95)',
  boxShadow: theme.palette.mode === 'dark'
    ? '0 8px 32px rgba(0, 0, 0, 0.3)'
    : '0 8px 32px rgba(0, 0, 0, 0.1)',
  '&:hover': {
    transform: 'translateY(-12px)',
    boxShadow: theme.palette.mode === 'dark'
      ? '0 20px 40px rgba(33, 150, 243, 0.3)'
      : '0 20px 40px rgba(33, 203, 243, 0.2)',
    borderColor: theme.palette.mode === 'dark' ? '#21CBF3' : '#2196F3',
  }
}));

const IconWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  marginBottom: theme.spacing(2),
  '& .MuiSvgIcon-root': {
    fontSize: '2.5rem',
    transition: 'all 0.3s ease-in-out',
    color: theme.palette.mode === 'dark' ? '#21CBF3' : '#2196F3',
  }
}));

const CategoryContainer = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
  gap: theme.spacing(3),
  width: '100%',
  padding: theme.spacing(0, 2),
  [theme.breakpoints.up('sm')]: {
    padding: 0,
  }
}));

const Section = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3, 0),
  position: 'relative',
  '&:nth-of-type(even)': {
    backgroundColor: theme.palette.mode === 'dark' 
      ? alpha(theme.palette.primary.main, 0.05)
      : alpha(theme.palette.primary.main, 0.02),
  }
}));

const FeatureCard = styled(Card)(({ theme }) => ({
  height: '100%',
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  textAlign: 'center',
  backgroundColor: theme.palette.background.paper,
  transition: 'all 0.3s ease-in-out',
  border: `1px solid ${theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
  borderRadius: '20px',
  backdropFilter: 'blur(10px)',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)'
    : 'rgba(255, 255, 255, 0.95)',
  boxShadow: theme.palette.mode === 'dark'
    ? '0 8px 32px rgba(0, 0, 0, 0.3)'
    : '0 8px 32px rgba(0, 0, 0, 0.1)',
  '&:hover': {
    transform: 'translateY(-10px)',
    boxShadow: theme.palette.mode === 'dark'
      ? '0 20px 40px rgba(33, 150, 243, 0.3)'
      : '0 20px 40px rgba(33, 203, 243, 0.2)',
    '& .MuiSvgIcon-root': {
      color: theme.palette.mode === 'dark' ? '#21CBF3' : '#2196F3',
      transform: 'scale(1.15)',
    }
  }
}));

const SectionTitle = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  color: theme.palette.mode === 'dark' ? '#fff' : '#333',
  marginBottom: theme.spacing(3),
  textAlign: 'center',
}));

const ProductSearch: React.FC = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const navigate = useNavigate();
  const [isLoaded, setIsLoaded] = useState(false);

  React.useEffect(() => {
    setIsLoaded(true);
  }, []);

  const handleCategorySelect = (category: string) => {
    navigate(`/category/${category}`);
  };

  const categories = [
    { 
      id: 'tv_video',
      icon: TvIcon,
      title: t('categories.tv_video'),
      description: t('categories.tv_video_desc')
    },
    { 
      id: 'audio',
      icon: AudioIcon,
      title: t('categories.audio'),
      description: t('categories.audio_desc')
    },
    { 
      id: 'mobile',
      icon: MobileIcon,
      title: t('categories.mobile'),
      description: t('categories.mobile_desc')
    },
    { 
      id: 'computers',
      icon: ComputersIcon,
      title: t('categories.computers'),
      description: t('categories.computers_desc')
    },
    { 
      id: 'home_appliances',
      icon: HomeAppliancesIcon,
      title: t('categories.home_appliances'),
      description: t('categories.home_appliances_desc')
    },
    { 
      id: 'kitchen_appliances',
      icon: KitchenAppliancesIcon,
      title: t('categories.kitchen_appliances'),
      description: t('categories.kitchen_appliances_desc')
    },
    { 
      id: 'climate',
      icon: HvacIcon,
      title: t('categories.climate'),
      description: t('categories.climate_desc')
    },
    { 
      id: 'healthcare',
      icon: HealthcareIcon,
      title: t('categories.healthcare'),
      description: t('categories.healthcare_desc')
    },
    { 
      id: 'lighting',
      icon: LightingIcon,
      title: t('categories.lighting'),
      description: t('categories.lighting_desc')
    },
    { 
      id: 'gaming',
      icon: GamingIcon,
      title: t('categories.gaming'),
      description: t('categories.gaming_desc')
    },
    { 
      id: 'cameras',
      icon: CameraIcon,
      title: t('categories.cameras'),
      description: t('categories.cameras_desc')
    },
    { 
      id: 'electronics',
      icon: ElectronicsIcon,
      title: t('categories.electronics'),
      description: t('categories.electronics_desc')
    }
  ];

  const features = [
    {
      icon: SearchIcon,
      title: t('features.easy_search.title'),
      description: t('features.easy_search.description')
    },
    {
      icon: ChatIcon,
      title: t('features.ai_assistant.title'),
      description: t('features.ai_assistant.description')
    },
    {
      icon: LightingIcon,
      title: t('features.smart_solutions.title'),
      description: t('features.smart_solutions.description')
    }
  ];

  return (
    <PageContainer>
      <Fade in={isLoaded} timeout={1000}>
        <HeroBanner>
          <Container maxWidth="md">
            <Typography
              variant="h2"
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 700,
                fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(45deg, #60A5FA 30%, #93C5FD 90%)'
                  : 'linear-gradient(45deg, #2563EB 30%, #3B82F6 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
              }}
            >
              {t('productSearch.welcome')}
            </Typography>
            <Typography
              variant="h5"
              sx={{
                maxWidth: '800px',
                margin: '0 auto',
                opacity: 0.9,
                fontSize: { xs: '1rem', sm: '1.1rem', md: '1.2rem' },
                lineHeight: 1.5,
                color: theme.palette.mode === 'dark' ? theme.palette.text.secondary : theme.palette.text.primary,
              }}
            >
              {t('productSearch.subtitle')}
            </Typography>
          </Container>
        </HeroBanner>
      </Fade>

      <Section>
        <Container maxWidth="lg">
          <SectionTitle variant="h4">
            {t('productSearch.byCategory')}
          </SectionTitle>
          
          <CategoryContainer>
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <CategoryCard key={category.id} elevation={theme.palette.mode === 'dark' ? 2 : 1}>
                  <CardActionArea
                    onClick={() => handleCategorySelect(category.id)}
                    sx={{ height: '100%', p: 2 }}
                  >
                    <CardContent sx={{ textAlign: 'center' }}>
                      <IconWrapper>
                        <Icon />
                      </IconWrapper>
                      <Typography
                        variant="h6"
                        component="h3"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        {category.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="textSecondary"
                        sx={{ opacity: 0.8 }}
                      >
                        {category.description}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </CategoryCard>
              );
            })}
          </CategoryContainer>
        </Container>
      </Section>

      <Section>
        <Container maxWidth="lg">
          <SectionTitle variant="h4">
            {t('productSearch.features')}
          </SectionTitle>
          
          <CategoryContainer>
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <FeatureCard key={index} elevation={theme.palette.mode === 'dark' ? 2 : 1}>
                  <IconWrapper>
                    <Icon />
                  </IconWrapper>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontWeight: 600 }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    sx={{ opacity: 0.8 }}
                  >
                    {feature.description}
                  </Typography>
                </FeatureCard>
              );
            })}
          </CategoryContainer>
        </Container>
      </Section>
    </PageContainer>
  );
};

export default ProductSearch; 