# Frontend Update Task List - PRIORITY
## Schema Enhancement Integration

### IMMEDIATE PRIORITY: Frontend is out of sync with backend!

The backend database schema has been significantly enhanced to support enterprise integration scenarios, but the frontend admin interface is completely unaware of these changes. This creates a critical gap where users cannot access or configure the new capabilities.

## 🚨 Critical Updates Required

### 1. TypeScript Interface Updates
Create/update interfaces in `frontend-new/src/lib/types/`:
```typescript
interface Service {
  // Existing fields...
  
  // New fields
  tool_type: 'API' | 'InternalAgent' | 'ExternalAgent' | 'ESBEndpoint' | 'LegacySystem' | 'MicroService';
  interaction_modes: string[];
  visibility: 'internal' | 'org-wide' | 'public' | 'restricted';
  deprecation_date?: string;
  deprecation_notice?: string;
  success_criteria?: object;
  default_timeout_ms: number;
  default_retry_policy?: object;
}

interface ServiceIntegrationDetails {
  id: number;
  service_id: number;
  access_protocol: string;
  base_endpoint?: string;
  auth_method?: string;
  auth_config?: object;
  rate_limit_requests?: number;
  rate_limit_window_seconds?: number;
  esb_type?: string;
  esb_service_name?: string;
  // ... other fields
}

interface ServiceAgentProtocol {
  id: number;
  service_id: number;
  message_protocol: string;
  protocol_version?: string;
  response_style?: string;
  supports_streaming?: boolean;
  // ... other fields
}
```

### 2. Service Management Form Updates
Update `frontend-new/src/routes/services/[id]/+page.svelte`:
- Add tool_type dropdown selector
- Add interaction_modes multi-select component
- Add visibility radio buttons
- Add collapsible sections for:
  - Integration Details
  - Agent Protocol (conditional on tool_type)
  - Industries
  - Deprecation Settings

### 3. New UI Components Needed
Create in `frontend-new/src/lib/components/`:
- `ServiceTypeSelector.svelte` - Visual selector for tool types
- `IntegrationDetailsForm.svelte` - Protocol and auth configuration
- `AgentProtocolForm.svelte` - Agent-specific settings
- `IndustryTagger.svelte` - Industry selection and relevance
- `AuthMethodConfigurator.svelte` - Dynamic auth configuration

### 4. API Client Updates
Update `frontend-new/src/lib/api/`:
- Add endpoints for integration details CRUD
- Add endpoints for agent protocols
- Add endpoints for industries
- Update service create/update to include new fields

### 5. Search Results Enhancement
Update `frontend-new/src/routes/search/+page.svelte`:
- Display tool_type as colored badges
- Show interaction modes as tags
- Indicate authentication requirements
- Display rate limits if applicable
- Show ESB routing info for ESB endpoints

### 6. Dashboard Updates
Update `frontend-new/src/routes/+page.svelte`:
- Add service type distribution chart
- Show integration protocol breakdown
- Display authentication method stats
- Add deprecation warnings widget

## Implementation Priority Order

### Week 1 - Core Updates (Days 1-3)
1. **Day 1**: Update TypeScript interfaces and API client
2. **Day 2**: Modify service create/edit forms with new fields
3. **Day 3**: Add integration details tab and form

### Week 1 - Enhanced Features (Days 4-5)
4. **Day 4**: Implement conditional UI for different tool_types
5. **Day 5**: Add agent protocol configuration for agent types

### Week 1 - Polish & Testing (Days 6-7)
6. **Day 6**: Update search results and dashboard
7. **Day 7**: Testing and bug fixes

## Example UI Mockup Structure

```
Service Edit Page
├── Basic Information
│   ├── Name, Description
│   ├── Tool Type [Dropdown]
│   ├── Interaction Modes [Multi-select]
│   └── Visibility [Radio]
├── Integration Details [Tab]
│   ├── Protocol Settings
│   ├── Authentication
│   ├── Rate Limiting
│   └── ESB Configuration [Conditional]
├── Agent Settings [Tab - Conditional]
│   ├── Message Protocol
│   ├── Response Style
│   └── Example Messages
├── Industries [Tab]
│   └── Industry Tags
└── Advanced [Tab]
    ├── Deprecation
    ├── Timeouts
    └── Retry Policy
```

## Backend API Updates Required

Before frontend can be updated, these API endpoints need enhancement:
- `GET/POST/PUT /api/v1/services/{id}` - Include all new fields
- `POST /api/v1/services/{id}/integration` - Manage integration details
- `POST /api/v1/services/{id}/agent-protocol` - Manage agent settings
- `GET /api/v1/services/tool-types` - List valid tool types
- `GET /api/v1/services/auth-methods` - List valid auth methods

## Success Criteria

- [ ] Users can create services with all tool types
- [ ] Integration details are properly saved and displayed
- [ ] Agent protocols can be configured for agent types
- [ ] Search results show enhanced metadata
- [ ] ESB configuration works for ESB endpoints
- [ ] Validation prevents invalid configurations
- [ ] Migration tool helps update existing services

## Resources Needed

- Frontend developer familiar with SvelteKit
- Understanding of the new schema structure
- API documentation for new endpoints
- Test data for different service types
- UI/UX guidelines for new components

## Risk Mitigation

- Create backwards compatibility layer
- Add feature flags for gradual rollout
- Provide migration wizard for existing services
- Include comprehensive validation
- Add help tooltips explaining new fields

---

**This is now the #1 priority task to unlock the value of the backend enhancements!**