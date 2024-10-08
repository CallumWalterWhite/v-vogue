import React, { useState } from 'react';
import { WebView } from 'react-native-webview';
import { API_BASE_URL } from '@/config';
import { View, ActivityIndicator } from 'react-native';

const GoogleLogin = () => {
  const [loading, setLoading] = useState(true);

  const handleNavigationStateChange = (navState: { url: string | string[]; }) => {
    if (navState.url.includes('/auth/google/callback')) {
        //TODO: Parse the URL to get the authorization code or tokens
    }
  };

  return (
    <View style={{ flex: 1 }}>
      {loading && <ActivityIndicator size="large" />}
      <WebView
        source={{ uri: `${API_BASE_URL}/security/login/google` }}
        onLoadEnd={() => setLoading(false)}
        onNavigationStateChange={handleNavigationStateChange}
      />
    </View>
  );
};

export default GoogleLogin;
